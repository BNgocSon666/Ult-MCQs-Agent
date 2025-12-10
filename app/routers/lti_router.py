import json
import secrets
import requests
from datetime import datetime
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from mariadb.connections import Connection  # Để type-hint

# === IMPORT MỚI CHO PYLTI1P3 (v2.x) ===
from pylti1p3.tool_config import ToolConfDict
from pylti1p3.oidc_login import OIDCLogin
from pylti1p3.message_launch import MessageLaunch
from pylti1p3.session import SessionService
from pylti1p3.cookie import CookieService
from pylti1p3.request import Request as PyltiRequest
from fastapi.responses import Response

# Import từ các file hiện có của bạn
from ..db import get_connection
from ..config import (
    APP_BASE_URL, LTI_CLIENT_ID, LTI_DEPLOYMENT_ID, LTI_AUTH_LOGIN_URL,
    LTI_AUTH_TOKEN_URL, LTI_KEY_SET_URL, LTI_PRIVATE_KEY_FILE, LTI_PUBLIC_KEY_FILE,
    REACT_BASE_URL,
    LTI_ISSUER_ID
)
from .auth_router import create_access_token, hash_password

router = APIRouter(prefix="/lti", tags=["LTI"])


# =========================================================================
# === 1. CẤU HÌNH LTI (ĐÃ SỬA LỖI) ====
# =========================================================================

def get_lti_config() -> ToolConfDict:
    """
    Đọc cấu hình LTI từ file config.py của bạn.
    Trả về một instance ToolConfDict cho pylti1p3 (v2.x).
    """
    try:
        with open(LTI_PRIVATE_KEY_FILE, 'r') as f_priv:
            private_key = f_priv.read()
        with open(LTI_PUBLIC_KEY_FILE, 'r') as f_pub:
            public_key = f_pub.read()
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc file LTI key: {e}")

    # === CẤU TRÚC CONFIG (DẠNG DICT) ===
    # Tạo một plain dict trước
    config_dict = {
        LTI_ISSUER_ID: [  # Key là Issuer ID
            {
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
    }
    
    # Khởi tạo ToolConfDict VỚI DỮ LIỆU
    return ToolConfDict(config_dict)


# -------------------------
# FastAPI adapters for pylti1p3
# -------------------------
class FastAPIRequestAdapter(PyltiRequest):
    """Adapter object that implements pylti1p3.request.Request for FastAPI's Request.

    We build it with a pre-parsed params dict (from form + query) so get_param can be sync.
    Also exposes a .session dict property used by SessionDataStorage.
    """

    def __init__(self, starlette_request: Request, params: dict):
        # store minimal pieces
        self._req = starlette_request
        # params is a plain dict of form+query params
        self._params = {k: v for k, v in params.items()}
        # provide a simple in-memory session mapping attached to request.state
        if not hasattr(self._req.state, "lti_session"):
            self._req.state.lti_session = {}

    @property
    def session(self):
        return self._req.state.lti_session

    def is_secure(self) -> bool:
        return self._req.url.scheme == "https"

    def get_param(self, key: str) -> str:
        # return as string or empty string if not present
        val = self._params.get(key)
        if val is None:
            return ""
        return str(val)


class FastAPICookieService(CookieService):
    """CookieService implementation that collects cookies to set on the final Response.

    It does not set cookies immediately; instead consumer (Redirect) will read cookie list
    and apply them to the Response before returning to client.
    """

    def __init__(self, starlette_request: Request):
        # read incoming cookies (dict-like)
        self._incoming = dict(starlette_request.cookies)
        self._to_set: list[tuple[str, str, int | None]] = []

    def get_cookie(self, name: str) -> str | None:
        return self._incoming.get(name)

    def set_cookie(self, name: str, value: str | int, exp: int | None = 3600):
        # store cookie to be set later by RedirectResponse
        self._to_set.append((name, str(value), exp))

    def get_outgoing(self) -> list[tuple[str, str, int | None]]:
        return self._to_set


class FastAPIRedirect:
    """Small Redirect wrapper used by our FastAPIOIDCLogin.get_redirect.

    It exposes do_redirect() which returns a FastAPI RedirectResponse with cookies applied.
    """

    def __init__(self, url: str, cookie_service: FastAPICookieService):
        self._url = url
        self._cookie_service = cookie_service

    def do_redirect(self) -> Response:
        resp = RedirectResponse(url=self._url)
        for name, value, exp in self._cookie_service.get_outgoing():
            # set cookie; if exp is None let it be session cookie
            if exp is None:
                resp.set_cookie(name, value)
            else:
                resp.set_cookie(name, value, max_age=exp)
        return resp

    def do_js_redirect(self) -> Response:
        return self.do_redirect()

    def set_redirect_url(self, location: str):
        self._url = location

    def get_redirect_url(self) -> str:
        return self._url

# =========================================================================
# === 2. HÀM HELPER (DATABASE & LOGIC) ===
# =========================================================================
# (Toàn bộ 2 hàm get_or_create_lti_user và create_lti_session
#  được giữ nguyên y hệt như code bạn đã dán ở trên)

def get_or_create_lti_user(conn: Connection, lti_data: dict) -> dict:
    # ... (Giữ nguyên code của bạn) ...
    lti_sub = lti_data.get('sub')
    email = lti_data.get('email', f"{lti_sub}@lti.user")
    full_name = lti_data.get('name', 'LTI User')
    username = email.split('@')[0] + "_" + secrets.token_hex(2)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Users WHERE lti_sub = %s", (lti_sub,))
    user = cur.fetchone()
    if user:
        cur.close()
        return user
    cur.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = cur.fetchone()
    if user:
        cur.execute("UPDATE Users SET lti_sub = %s WHERE user_id = %s", (lti_sub, user['user_id']))
        conn.commit()
        cur.close()
        return user
    random_password = secrets.token_hex(16)
    hashed_password = hash_password(random_password)
    cur.execute("""
        INSERT INTO Users (username, email, full_name, password_hash, lti_sub, is_active)
        VALUES (%s, %s, %s, %s, %s, 1)
    """, (username, email, full_name, hashed_password, lti_sub))
    new_user_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM Users WHERE user_id = %s", (new_user_id,))
    new_user = cur.fetchone()
    cur.close()
    return new_user

def create_lti_session(conn: Connection, exam_id: int, user_id: int, lti_data: dict) -> int:
    # ... (Giữ nguyên code của bạn) ...
    ags_data = lti_data.get('https://purl.imsglobal.org/spec/lti-ags/claim/endpoint', {})
    lineitem_url = ags_data.get('lineitem')
    lti_sub = lti_data.get('sub')
    lti_iss = lti_data.get('iss')
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
# === 3. CÁC ENDPOINTS LTI (ĐÃ SỬA) ===
# =========================================================================

@router.get("/jwks")
def get_jwks():
    """
    Endpoint (Công khai)
    LMS (Moodle/Canvas) sẽ gọi đây để lấy public key của bạn.
    """
    try:
        config = get_lti_config()
        # Lấy JWKS từ issuer đầu tiên (và duy nhất)
        issuer = list(config.get_issuers())[0]
        return config.get_jwks(issuer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi LTI JWKS: {str(e)}")

# [FILE: lti_router.py]

# Sửa dòng này: Chấp nhận cả GET và POST
@router.api_route("/login", methods=["GET", "POST"]) 
async def lti_login(request: Request):
    """
    Endpoint (Công khai)
    Điểm bắt đầu của OIDC (OpenID Connect).
    """
    try:
        config = get_lti_config()
        target_link_uri = f"{APP_BASE_URL}/lti/launch"

        # Lấy dữ liệu từ cả Form (POST) và Query Params (GET)
        # Vì Moodle gửi các tham số như iss, login_hint qua URL (GET)
        if request.method == "POST":
            form_data = await request.form()
            params = dict(form_data)
        else:
            params = {}
            
        # Luôn cập nhật thêm query params (quan trọng cho GET)
        params.update({k: v for k, v in request.query_params.items()})

        # Adapter + services cho pylti1p3
        adapter = FastAPIRequestAdapter(request, params)
        session_service = SessionService(adapter)
        cookie_service = FastAPICookieService(request)

        class FastAPIOIDCLogin(OIDCLogin):
            def get_redirect(self, url: str) -> FastAPIRedirect:
                return FastAPIRedirect(url, cookie_service)

        oidc_login = FastAPIOIDCLogin(adapter, config, session_service, cookie_service)
        return oidc_login.redirect(target_link_uri)

    except Exception as e:
        print(f"LỖI LTI LOGIN: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi LTI Login: {str(e)}")

# [FILE: lti_router.py]

@router.post("/launch")
async def lti_launch(request: Request, conn=Depends(get_connection)):
    """
    Endpoint (Công khai)
    Đây là điểm vào chính sau khi xác thực.
    """
    try:
        config = get_lti_config()
        
        # 1. CHUẨN BỊ DỮ LIỆU
        form_data = await request.form()
        params = dict(form_data)
        params.update({k: v for k, v in request.query_params.items()})

        # Tạo Adapter (Chứa session)
        adapter = FastAPIRequestAdapter(request, params)

        # 2. XÁC THỰC MESSAGE LAUNCH (ĐÃ SỬA DÒNG NÀY)
        # Truyền trực tiếp adapter và config
        message_launch = MessageLaunch(adapter, config)
        
        # Hàm này sẽ tự động kiểm tra chữ ký, nonce, state từ session...
        lti_data = message_launch.get_launch_data()
        
        # -------------------------------------------------------------
        # 3. XỬ LÝ NGHIỆP VỤ (GIỮ NGUYÊN)
        # -------------------------------------------------------------
        
        # A. Xác định và cấp phép User (SSO)
        user = get_or_create_lti_user(conn, lti_data)
        user_id = user["user_id"]
        
        # B. Tạo JWT Token
        access_token = create_access_token(data={
            "sub": user["username"], 
            "user_id": user_id, 
            "is_admin": user.get("is_admin", 0)
        })
        
        # C. Kiểm tra vai trò
        roles = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        is_instructor = "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor" in roles
        
        # D. Điều hướng
        if is_instructor:
            redirect_url = f"{REACT_BASE_URL}/dashboard/agent?token={access_token}"
            return RedirectResponse(url=redirect_url)

        # Học sinh
        custom_params = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {})
        exam_share_token = custom_params.get('exam_share_token')
        
        if not exam_share_token:
            print("LTI Warning: Thiếu exam_share_token, chuyển hướng về Dashboard")
            return RedirectResponse(url=f"{REACT_BASE_URL}/dashboard?token={access_token}")
            
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT exam_id FROM Exams WHERE share_token = %s", (exam_share_token,))
        exam = cur.fetchone()
        cur.close()
        
        if not exam:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy Exam: {exam_share_token}")
        
        session_id = create_lti_session(conn, exam['exam_id'], user_id, lti_data)
        
        redirect_url = f"{REACT_BASE_URL}/session/{session_id}?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        print(f"LỖI LTI LAUNCH: {e}")
        # In chi tiết lỗi ra console server để debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Lỗi xác thực LTI: {str(e)}")


# =========================================================================
# === 4. HÀM GỬI ĐIỂM (GRADE PASSBACK) (ĐÃ SỬA) ===
# =========================================================================

def submit_grade_lti(session_id: int, total_score: int, total_questions: int, conn: Connection):
    """
    Hàm này được gọi từ sessions_router.py (sau khi chấm bài).
    Gửi điểm về LMS (v2.x).
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
        print(f"[LTI] Session {session_id} không phải LTI. Bỏ qua gửi điểm.")
        return

    try:
        config = get_lti_config()
        issuer_id = session_data['lti_iss']
        
        # Lấy service client đã được xác thực
        service_client_factory = config.get_service_client_factory(issuer_id, LTI_CLIENT_ID)
        service_client = service_client_factory.make_client()
        
        # Tính điểm (thang 0.0 -> 1.0)
        score_decimal = (total_score / total_questions) if total_questions > 0 else 0
        
        lineitem_url = session_data['lti_lineitem_url']
        
        score_payload = {
            "scoreGiven": score_decimal,
            "scoreMaximum": 1.0,
            "activityProgress": "Completed",
            "gradingProgress": "FullyGraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "userId": session_data['lti_user_sub']
        }
        
        # Gửi điểm (Sử dụng hàm của service_client)
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