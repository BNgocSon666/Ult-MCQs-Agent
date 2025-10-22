USE [master]
GO
/****** Object:  Database [Ultimate_MCQs_Agent]    Script Date: 10/22/2025 1:29:29 PM ******/
CREATE DATABASE [Ultimate_MCQs_Agent]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'Ultimate_MCQs_Agent', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\Ultimate_MCQs_Agent.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'Ultimate_MCQs_Agent_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\Ultimate_MCQs_Agent_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [Ultimate_MCQs_Agent].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ARITHABORT OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET  DISABLE_BROKER 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET RECOVERY FULL 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET  MULTI_USER 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET DB_CHAINING OFF 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'Ultimate_MCQs_Agent', N'ON'
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET QUERY_STORE = ON
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [Ultimate_MCQs_Agent]
GO
/****** Object:  User [thuan]    Script Date: 10/22/2025 1:29:29 PM ******/
CREATE USER [thuan] WITHOUT LOGIN WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER ROLE [db_owner] ADD MEMBER [thuan]
GO
ALTER ROLE [db_ddladmin] ADD MEMBER [thuan]
GO
ALTER ROLE [db_datawriter] ADD MEMBER [thuan]
GO
/****** Object:  Table [dbo].[ExamQuestions]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ExamQuestions](
	[exam_question_id] [int] IDENTITY(1,1) NOT NULL,
	[exam_id] [int] NOT NULL,
	[question_id] [int] NOT NULL,
	[order_index] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[exam_question_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[exam_id] ASC,
	[question_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Exams]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Exams](
	[exam_id] [int] IDENTITY(1,1) NOT NULL,
	[owner_id] [int] NOT NULL,
	[title] [nvarchar](500) NOT NULL,
	[description] [nvarchar](max) NULL,
	[share_token] [varchar](50) NOT NULL,
	[is_public] [bit] NULL,
	[created_at] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[exam_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[share_token] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ExamSessions]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ExamSessions](
	[session_id] [int] IDENTITY(1,1) NOT NULL,
	[exam_id] [int] NOT NULL,
	[user_id] [int] NULL,
	[guest_name] [nvarchar](255) NULL,
	[start_time] [datetime] NULL,
	[end_time] [datetime] NULL,
	[total_score] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[session_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Files]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Files](
	[file_id] [int] IDENTITY(1,1) NOT NULL,
	[uploader_id] [int] NOT NULL,
	[filename] [nvarchar](500) NOT NULL,
	[file_type] [varchar](50) NOT NULL,
	[uploaded_at] [datetime] NULL,
	[storage_path] [varchar](500) NULL,
	[raw_text] [nvarchar](max) NULL,
	[summary] [nvarchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[file_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[QuestionEvaluations]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[QuestionEvaluations](
	[evaluation_id] [int] IDENTITY(1,1) NOT NULL,
	[question_id] [int] NOT NULL,
	[model_version] [varchar](100) NOT NULL,
	[evaluated_at] [datetime] NULL,
	[total_score] [int] NOT NULL,
	[accuracy_score] [int] NULL,
	[alignment_score] [int] NULL,
	[distractors_score] [int] NULL,
	[clarity_score] [int] NULL,
	[status_by_agent] [varchar](20) NULL,
	[raw_response_json] [nvarchar](max) NULL,
PRIMARY KEY CLUSTERED 
(
	[evaluation_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Questions]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Questions](
	[question_id] [int] IDENTITY(1,1) NOT NULL,
	[source_file_id] [int] NULL,
	[creator_id] [int] NULL,
	[latest_evaluation_id] [int] NULL,
	[question_text] [nvarchar](max) NOT NULL,
	[options] [nvarchar](max) NOT NULL,
	[answer_letter] [char](1) NOT NULL,
	[status] [varchar](20) NOT NULL,
	[created_at] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[question_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[SessionResults]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SessionResults](
	[result_id] [int] IDENTITY(1,1) NOT NULL,
	[session_id] [int] NOT NULL,
	[question_id] [int] NOT NULL,
	[selected_option] [char](1) NULL,
	[is_correct] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[result_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[session_id] ASC,
	[question_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Users]    Script Date: 10/22/2025 1:29:29 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[user_id] [int] IDENTITY(1,1) NOT NULL,
	[username] [nvarchar](255) NOT NULL,
	[email] [varchar](255) NOT NULL,
	[password_hash] [varchar](255) NOT NULL,
	[created_at] [datetime] NULL,
	[is_active] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[user_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[username] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Exams] ADD  DEFAULT ((0)) FOR [is_public]
GO
ALTER TABLE [dbo].[Exams] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[ExamSessions] ADD  DEFAULT (getdate()) FOR [start_time]
GO
ALTER TABLE [dbo].[Files] ADD  DEFAULT (getdate()) FOR [uploaded_at]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT (getdate()) FOR [evaluated_at]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT ((0)) FOR [accuracy_score]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT ((0)) FOR [alignment_score]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT ((0)) FOR [distractors_score]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT ((0)) FOR [clarity_score]
GO
ALTER TABLE [dbo].[QuestionEvaluations] ADD  DEFAULT ('need_review') FOR [status_by_agent]
GO
ALTER TABLE [dbo].[Questions] ADD  DEFAULT ('TEMP') FOR [status]
GO
ALTER TABLE [dbo].[Questions] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT ((1)) FOR [is_active]
GO
ALTER TABLE [dbo].[ExamQuestions]  WITH CHECK ADD FOREIGN KEY([exam_id])
REFERENCES [dbo].[Exams] ([exam_id])
GO
ALTER TABLE [dbo].[ExamQuestions]  WITH CHECK ADD FOREIGN KEY([question_id])
REFERENCES [dbo].[Questions] ([question_id])
GO
ALTER TABLE [dbo].[Exams]  WITH CHECK ADD FOREIGN KEY([owner_id])
REFERENCES [dbo].[Users] ([user_id])
GO
ALTER TABLE [dbo].[ExamSessions]  WITH CHECK ADD FOREIGN KEY([exam_id])
REFERENCES [dbo].[Exams] ([exam_id])
GO
ALTER TABLE [dbo].[ExamSessions]  WITH CHECK ADD FOREIGN KEY([user_id])
REFERENCES [dbo].[Users] ([user_id])
GO
ALTER TABLE [dbo].[Files]  WITH CHECK ADD FOREIGN KEY([uploader_id])
REFERENCES [dbo].[Users] ([user_id])
GO
ALTER TABLE [dbo].[QuestionEvaluations]  WITH CHECK ADD FOREIGN KEY([question_id])
REFERENCES [dbo].[Questions] ([question_id])
GO
ALTER TABLE [dbo].[Questions]  WITH CHECK ADD FOREIGN KEY([creator_id])
REFERENCES [dbo].[Users] ([user_id])
GO
ALTER TABLE [dbo].[Questions]  WITH CHECK ADD FOREIGN KEY([source_file_id])
REFERENCES [dbo].[Files] ([file_id])
GO
ALTER TABLE [dbo].[Questions]  WITH CHECK ADD  CONSTRAINT [FK_LatestEvaluation] FOREIGN KEY([latest_evaluation_id])
REFERENCES [dbo].[QuestionEvaluations] ([evaluation_id])
GO
ALTER TABLE [dbo].[Questions] CHECK CONSTRAINT [FK_LatestEvaluation]
GO
ALTER TABLE [dbo].[SessionResults]  WITH CHECK ADD FOREIGN KEY([question_id])
REFERENCES [dbo].[Questions] ([question_id])
GO
ALTER TABLE [dbo].[SessionResults]  WITH CHECK ADD FOREIGN KEY([session_id])
REFERENCES [dbo].[ExamSessions] ([session_id])
GO
ALTER TABLE [dbo].[ExamSessions]  WITH CHECK ADD  CONSTRAINT [CHK_UserOrGuest] CHECK  (([user_id] IS NULL AND [guest_name] IS NOT NULL OR [user_id] IS NOT NULL AND [guest_name] IS NULL))
GO
ALTER TABLE [dbo].[ExamSessions] CHECK CONSTRAINT [CHK_UserOrGuest]
GO
USE [master]
GO
ALTER DATABASE [Ultimate_MCQs_Agent] SET  READ_WRITE 
GO
