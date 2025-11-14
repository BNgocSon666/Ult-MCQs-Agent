import json
import secrets
import requests
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.oidc_login import OIDCLogin
from pylti1p3.message_launch import MessageLaunch
from mariadb.connections import Connection # Để type-hint

# Import từ các file hiện có của bạn
from ..db import get_connection
from ..config import (
    APP_BASE_URL, LTI_CLIENT_ID, LTI_DEPLOYMENT_ID, LTI_AUTH_LOGIN_URL,
    LTI_AUTH_TOKEN_URL, LTI_KEY_SET_URL, LTI_PRIVATE_KEY_FILE, LTI_PUBLIC_KEY_FILE,
    REACT_BASE_URL,  # <-- Bạn đã thêm cái này
    LTI_ISSUER_ID    # <-- THÊM DÒNG NÀY
)
from .auth_router import create_access_token, hash_password

router = APIRouter(prefix="/lti", tags=["LTI"])


# =========================================================================
# === 1. CẤU HÌNH LTI ===
# =========================================================================

def get_lti_config():
    """
    Đọc cấu hình LTI từ file config.py của bạn.
    Sử dụng cấu trúc config mới để tránh lỗi "Key 'client_id' is missing".
    """
    conf = ToolConf()
    
    try:
        with open(LTI_PRIVATE_KEY_FILE, 'r') as f_priv:
            private_key = f_priv.read()
        with open(LTI_PUBLIC_KEY_FILE, 'r') as f_pub:
            public_key = f_pub.read()
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc file LTI key: {e}")

    # === CẤU TRÚC CONFIG MỚI ===
    # Cấu hình này chỉ rõ:
    # "Đối với issuer [LTI_ISSUER_ID], hãy dùng client_id [LTI_CLIENT_ID] và các URL/Key này"
    issuers_config = [
        {
            "issuer": LTI_ISSUER_ID,  # (ví dụ: https://...moodlecloud.com)
            "client_id": LTI_CLIENT_ID,
            "auth_login_url": LTI_AUTH_LOGIN_URL,
            "auth_token_url": LTI_AUTH_TOKEN_URL,
            "key_set_url": LTI_KEY_SET_URL,
            "deployment_ids": [LTI_DEPLOYMENT_ID],
            "auth_key": private_key,
            "pub_key": public_key,
            "auth_method": "JWK-RSA",
            "auth_alg": "RS256"
        }
    ]
    
    conf.set_issuers_config(issuers_config)
    return conf

# =========================================================================
# === 2. HÀM HELPER (DATABASE & LOGIC) ===
# =========================================================================

def get_or_create_lti_user(conn: Connection, lti_data: dict) -> dict:
    """
    Tìm user trong CSDL bằng lti_sub.
    Nếu không thấy, tạo user mới.
    Trả về thông tin user (dạng dict).
    """
    # lti_data['sub'] là ID duy nhất của user từ LMS
    lti_sub = lti_data.get('sub')
    email = lti_data.get('email', f"{lti_sub}@lti.user")
    full_name = lti_data.get('name', 'LTI User')
    username = email.split('@')[0] + "_" + secrets.token_hex(2) # Tên username tạm

    cur = conn.cursor(dictionary=True)
    
    # 1. Thử tìm bằng LTI sub
    cur.execute("SELECT * FROM Users WHERE lti_sub = %s", (lti_sub,))
    user = cur.fetchone()
    if user:
        cur.close()
        return user

    # 2. Thử tìm bằng email (Nếu user đã đăng ký bằng email này)
    cur.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        # Tìm thấy! Cập nhật lti_sub để lần sau tìm nhanh hơn
        cur.execute("UPDATE Users SET lti_sub = %s WHERE user_id = %s", (lti_sub, user['user_id']))
        conn.commit()
        cur.close()
        return user
        
    # 3. Không thấy -> Tạo user mới
    # Tạo mật khẩu ngẫu nhiên (vì LTI không cung cấp)
    random_password = secrets.token_hex(16)
    hashed_password = hash_password(random_password) # Dùng hàm từ auth_router.py

    cur.execute("""
        INSERT INTO Users (username, email, full_name, password_hash, lti_sub, is_active)
        VALUES (%s, %s, %s, %s, %s, 1)
    """, (username, email, full_name, hashed_password, lti_sub))
    
    new_user_id = cur.lastrowid
    conn.commit()
    
    # Lấy lại thông tin user vừa tạo
    cur.execute("SELECT * FROM Users WHERE user_id = %s", (new_user_id,))
    new_user = cur.fetchone()
    cur.close()
    return new_user

def create_lti_session(conn: Connection, exam_id: int, user_id: int, lti_data: dict) -> int:
    """
    Tạo một ExamSession MỚI, lưu kèm thông tin LTI để gửi điểm.
    Trả về (int) session_id mới.
    """
    # Lấy thông tin cần thiết để gửi điểm
    # AGS = Assignment and Grade Services
    ags_data = lti_data.get('https://purl.imsglobal.org/spec/lti-ags/claim/endpoint', {})
    lineitem_url = ags_data.get('lineitem') # URL để gửi điểm
    lti_sub = lti_data.get('sub') # ID của user
    lti_iss = lti_data.get('iss') # ID của LMS
    
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ExamSessions 
            (exam_id, user_id, start_time, lti_lineitem_url, lti_user_sub, lti_iss)
        VALUES (%s, %s, NOW(), %s, %s, %s)
    """, (exam_id, user_id, lineitem_url, lti_sub, lti_iss))
    
    session_id = cur.lastrowid
    conn.commit()
    cur.close()
    return session_id

# =========================================================================
# === 3. CÁC ENDPOINTS LTI (CỬA VÀO) ===
# =========================================================================

@router.get("/jwks")
def get_jwks():
    """
    Endpoint (Công khai)
    LMS (Moodle/Canvas) sẽ gọi đây để lấy public key của bạn.
    """
    try:
        config = get_lti_config()
        return config.get_jwks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi LTI JWKS: {str(e)}")

@router.post("/login")
async def lti_login(request: Request):
    """
    Endpoint (Công khai)
    Điểm bắt đầu của OIDC (OpenID Connect).
    LMS sẽ gọi đây trước.
    """
    try:
        config = get_lti_config()
        
        # Tạo URL để LMS chuyển hướng người dùng đến (chính là /launch)
        target_link_uri = f"{APP_BASE_URL}/lti/launch" 
        
        # Lấy thông tin từ request
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Khởi tạo OIDC login
        oidc_login = OIDCLogin(request_data, config)
        redirect_url = oidc_login.get_redirect_url(target_link_uri)
        return RedirectResponse(url=redirect_url)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi LTI Login: {str(e)}")

@router.post("/launch")
async def lti_launch(request: Request, conn=Depends(get_connection)):
    """
    Endpoint (Công khai)
    Đây là điểm vào chính sau khi xác thực.
    LMS chuyển hướng người dùng đến đây.
    """
    config = get_lti_config()
    
    try:
        # Lấy dữ liệu từ request (JWT được LMS gửi)
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Xác thực launch message
        message_launch = MessageLaunch(request_data, config)
        lti_data = message_launch.get_launch_data()
        
        # 2. Xác định và cấp phép User (SSO)
        user = get_or_create_lti_user(conn, lti_data)
        user_id = user["user_id"]
        
        # 3. Tạo JWT Token (của ứng dụng bạn)
        # Dùng hàm từ auth_router.py
        access_token = create_access_token(data={
            "sub": user["username"], 
            "user_id": user_id, 
            "is_admin": user.get("is_admin", 0)
        })
        
        # 4. Kiểm tra vai trò (Giáo viên hay Học sinh?)
        roles = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        is_instructor = "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor" in roles
        
        # ==================
        # 4A. NẾU LÀ GIÁO VIÊN (VÀO DASHBOARD)
        # ==================
        if is_instructor:
            # Chuyển hướng đến React Dashboard, đính kèm JWT
            # Frontend (AuthContext.jsx) cần được cập nhật để đọc token từ URL
            redirect_url = f"{APP_BASE_URL.replace('api.', '')}/dashboard/agent?token={access_token}"
            return RedirectResponse(url=redirect_url)

        # ==================
        # 4B. NẾU LÀ HỌC SINH (VÀO LÀM BÀI)
        # ==================
        
        # Giáo viên phải cấu hình `share_token` trong LMS
        custom_params = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {})
        exam_share_token = custom_params.get('exam_share_token')
        
        if not exam_share_token:
            raise HTTPException(status_code=400, detail="LTI launch (Learner) bị thiếu 'exam_share_token' trong Custom Parameters.")
            
        # Lấy exam_id từ share_token
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exam_id FROM Exams WHERE share_token = %s", (exam_share_token,))
        exam = cur.fetchone()
        cur.close()
        
        if not exam:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy Exam với share_token: {exam_share_token}")
        
        # Tạo phiên làm bài MỚI, lưu thông tin LTI
        session_id = create_lti_session(conn, exam['exam_id'], user_id, lti_data)
        
        # Chuyển hướng thẳng đến trang làm bài, đính kèm JWT
        redirect_url = f"{APP_BASE_URL.replace('api.', '')}/session/{session_id}?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        conn.rollback() # Hoàn tác nếu có lỗi CSDL
        print(f"LỖI LTI LAUNCH NGHIÊM TRỌNG: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ LTI Launch: {str(e)}")


# =========================================================================
# === 4. HÀM GỬI ĐIỂM (GRADE PASSBACK) ===
# =========================================================================

def submit_grade_lti(session_id: int, total_score: int, total_questions: int, conn: Connection):
    """
    Hàm này được gọi từ sessions_router.py (sau khi chấm bài).
    Nó lấy thông tin LTI đã lưu và gửi điểm về LMS.
    """
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT lti_lineitem_url, lti_user_sub, lti_iss 
        FROM ExamSessions 
        WHERE session_id = %s
    """, (session_id,))
    session_data = cur.fetchone()
    cur.close()

    if not session_data or not session_data.get('lti_lineitem_url'):
        # Đây là 1 session bình thường (không phải LTI), bỏ qua
        print(f"[LTI] Session {session_id} không phải LTI. Bỏ qua gửi điểm.")
        return

    try:
        config = get_lti_config()
        
        # Tính điểm (thang 0.0 -> 1.0)
        score_decimal = (total_score / total_questions) if total_questions > 0 else 0
        
        # Dùng thư viện pylti1p3 để lấy "access token" của LMS
        # (Token này khác với JWT token của bạn)
        service_client = config.get_service_client(LTI_CLIENT_ID)
        
        # URL để gửi điểm (đã lưu khi launch)
        lineitem_url = session_data['lti_lineitem_url']
        
        # Dữ liệu payload theo chuẩn LTI
        score_payload = {
            "scoreGiven": score_decimal,
            "scoreMaximum": 1.0,
            "activityProgress": "Completed",
            "gradingProgress": "FullyGraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "userId": session_data['lti_user_sub']
        }
        
        # Gửi điểm
        # (Lưu ý: lineitem_url có thể chứa 'scores' hoặc không, logic này xử lý cả hai)
        if '/scores' not in lineitem_url:
            lineitem_url = lineitem_url.rstrip('/') + '/scores'
            
        response = service_client.post(
            lineitem_url,
            data=json.dumps(score_payload),
            headers={'Content-Type': 'application/vnd.ims.lis.v1.score+json'}
        )
        
        if response.status_code == 200:
            print(f"[LTI] Gửi điểm thành công cho session {session_id}!")
        else:
            print(f"[LTI] Lỗi gửi điểm: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[LTI] Lỗi nghiêm trọng khi gửi điểm: {str(e)}")