import os
import shutil
import tempfile
from pathlib import Path

import streamlit as st

from ai_solver import (
    analyze_code_error,
    generate_learning_plan,
    run_user_code,
    save_outputs,
    transcribe_from_image,
    transcribe_problem_text,
)
from github_utils import commit_all, has_git, init_repo_if_needed, push, set_remote

st.set_page_config(
    page_title="Python Study Assistant",
    page_icon="🐍",
    layout="wide",
)

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_BANNER = PROJECT_DIR / "assets" / "banner.png"
OUTPUT_DIR = PROJECT_DIR / "outputs"
EXPORT_DIR = PROJECT_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

CSS = """
<style>
:root {
    --bg-1: #0f172a;
    --bg-2: #111827;
    --card: rgba(17, 24, 39, 0.78);
    --card-2: rgba(15, 23, 42, 0.82);
    --border: rgba(99, 102, 241, 0.22);
    --text: #e5eefb;
    --muted: #b8c4dd;
    --accent: #60a5fa;
    --accent-2: #818cf8;
    --success: #10b981;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #13203d 0%, var(--bg-1) 45%, #0b1220 100%);
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

h1, h2, h3, h4, p, label, div, span {
    color: var(--text);
}

.hero-card, .section-card {
    background: linear-gradient(180deg, var(--card) 0%, var(--card-2) 100%);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.1rem 1.15rem;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.22);
    margin-bottom: 1rem;
}

.small-note {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.5;
}

.badge {
    display: inline-block;
    padding: 0.32rem 0.72rem;
    border-radius: 999px;
    background: rgba(96, 165, 250, 0.14);
    color: #dbeafe;
    border: 1px solid rgba(96, 165, 250, 0.26);
    margin-right: 0.45rem;
    margin-bottom: 0.45rem;
    font-size: 0.88rem;
}

.note-box {
    border-left: 4px solid var(--accent);
    background: rgba(30, 41, 59, 0.72);
    padding: 0.8rem 1rem;
    border-radius: 12px;
    color: #dbeafe;
    margin-top: 0.6rem;
}

[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: rgba(248, 250, 252, 0.96) !important;
    color: #0f172a !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148, 163, 184, 0.24) !important;
}

[data-testid="stTextArea"] textarea {
    line-height: 1.55 !important;
    font-size: 15px !important;
}

.stButton > button {
    border-radius: 14px !important;
    border: none !important;
    padding: 0.62rem 1rem !important;
    font-weight: 600 !important;
}

.result-ok {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    color: #d1fae5;
    margin-top: 0.7rem;
}

.file-preview {
    color: #cbd5e1;
    font-size: 0.92rem;
    margin-top: 0.35rem;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

if "lesson" not in st.session_state:
    st.session_state.lesson = None
if "problem_text" not in st.session_state:
    st.session_state.problem_text = ""
if "zip_path" not in st.session_state:
    st.session_state.zip_path = None
if "user_code" not in st.session_state:
    st.session_state.user_code = ""
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = ""
if "run_result" not in st.session_state:
    st.session_state.run_result = None


def zip_project(project_dir: Path, export_dir: Path) -> str:
    zip_base = export_dir / "python_study_assistant_export"
    if zip_base.with_suffix(".zip").exists():
        zip_base.with_suffix(".zip").unlink()

    shutil.make_archive(str(zip_base), "zip", root_dir=str(project_dir), base_dir=".")
    return str(zip_base.with_suffix(".zip"))


def preview_file_name(name: str) -> str:
    if not name.strip():
        return "solution"
    cleaned = name.replace(".", "_")
    cleaned = "".join(ch if ch.isalnum() or ch in ["_", "-"] else "_" for ch in cleaned)
    cleaned = cleaned.strip("_").lower()
    return cleaned or "solution"


with st.container():
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    col_a, col_b = st.columns([1.2, 0.9])
    with col_a:
        st.title("🐍 Python Study Assistant")
        st.write(
            "Nhập đề bài, nhận gợi ý dễ hiểu, tự viết code, chạy thử và để AI giải thích lỗi từng bước."
        )
        st.markdown(
            '<span class="badge">Gợi ý dễ hiểu</span>'
            '<span class="badge">Code khung</span>'
            '<span class="badge">Tự nhập code</span>'
            '<span class="badge">AI chỉ lỗi</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="note-box"><b>Lưu ý:</b> App ưu tiên học tập. AI chỉ đưa gợi ý và phân tích lỗi, không tự viết toàn bộ bài cho bạn.</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        if ASSET_BANNER.exists():
            st.image(str(ASSET_BANNER), use_container_width=True)
        else:
            st.markdown(
                '<div class="small-note">Bạn có thể thêm ảnh banner vào thư mục <code>assets/banner.png</code>.</div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("1) Nhập đề bài")

    input_mode = st.radio(
        "Chọn cách đưa đề bài",
        ["Nhập văn bản", "Tải ảnh đề bài"],
        horizontal=True,
    )

    if input_mode == "Nhập văn bản":
        problem_text = st.text_area(
            "Dán đề bài Python",
            value=st.session_state.problem_text,
            height=200,
            placeholder="Ví dụ: Nhập 2 số nguyên và in ra tổng của chúng...",
        )
        if st.button("Lưu đề bài", use_container_width=True):
            st.session_state.problem_text = transcribe_problem_text(problem_text)
            st.success("Đã lưu đề bài.")
    else:
        uploaded_file = st.file_uploader("Chọn ảnh đề bài", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Ảnh đề bài đã tải lên", use_container_width=True)
            if st.button("Trích nội dung từ ảnh", use_container_width=True):
                suffix = Path(uploaded_file.name).suffix or ".png"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                try:
                    extracted = transcribe_from_image(tmp_path)
                    st.session_state.problem_text = extracted
                    st.success("Đã trích nội dung từ ảnh.")
                except Exception as e:
                    st.error(f"Lỗi đọc ảnh: {e}")
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

    st.text_area(
        "Nội dung đề bài hiện tại",
        value=st.session_state.problem_text,
        height=180,
        key="preview_problem_text",
    )

    extra_request = st.text_input(
        "Yêu cầu thêm",
        placeholder="Ví dụ: dễ hiểu cho người mới, chỉ cho gợi ý trước",
    )

    if st.button("✨ Tạo gợi ý học tập", type="primary", use_container_width=True):
        if not st.session_state.problem_text.strip():
            st.error("Bạn cần nhập đề bài hoặc trích đề từ ảnh trước.")
        else:
            try:
                with st.spinner("AI đang tạo gợi ý..."):
                    st.session_state.lesson = generate_learning_plan(
                        st.session_state.problem_text,
                        extra_request,
                    )
                    st.session_state.user_code = st.session_state.lesson.get("starter_code", "")
                    st.session_state.ai_feedback = ""
                    st.session_state.run_result = None
                st.success("Đã tạo gợi ý và code khung.")
            except Exception as e:
                st.error(f"Lỗi tạo gợi ý: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("2) Học và viết code")

    if st.session_state.lesson:
        lesson = st.session_state.lesson

        st.markdown(f"### {lesson.get('title', 'Huong dan Python')}")
        if lesson.get("summary"):
            st.write(lesson.get("summary", ""))

        with st.expander("Giải thích dễ hiểu", expanded=True):
            st.write(lesson.get("explanation_easy", "") or "Chưa có giải thích.")

        with st.expander("Gợi ý mức 1", expanded=True):
            hints_1 = lesson.get("hint_level_1", [])
            if hints_1:
                for item in hints_1:
                    st.write(f"- {item}")
            else:
                st.write("Chưa có gợi ý mức 1.")

        with st.expander("Gợi ý mức 2"):
            hints_2 = lesson.get("hint_level_2", [])
            if hints_2:
                for item in hints_2:
                    st.write(f"- {item}")
            else:
                st.write("Chưa có gợi ý mức 2.")

        tests = lesson.get("sample_tests", [])
        if tests:
            with st.expander("Ví dụ test"):
                for i, t in enumerate(tests, start=1):
                    st.markdown(f"**Test {i}**")
                    st.code(
                        f"Input:\n{t.get('input', '')}\n\nOutput mong doi:\n{t.get('output', '')}",
                        language="text",
                    )

        st.text_area(
            "3) Code khung / code của bạn",
            value=st.session_state.user_code,
            height=300,
            key="user_code_editor",
        )
        st.session_state.user_code = st.session_state.user_code_editor

        default_input = tests[0].get("input", "") if tests else ""
        expected_output = tests[0].get("output", "") if tests else ""

        manual_input = st.text_area(
            "Input để chạy thử",
            value=default_input,
            height=110,
            key="manual_test_input",
        )

        btn_col_1, btn_col_2 = st.columns(2)

        with btn_col_1:
            if st.button("▶ Chạy thử code", use_container_width=True):
                result = run_user_code(st.session_state.user_code, manual_input)
                st.session_state.run_result = result

                if result["ok"]:
                    st.success("Code đã chạy xong.")
                else:
                    st.error("Code đang có lỗi khi chạy.")

        with btn_col_2:
            if st.button("🧠 AI phân tích lỗi", use_container_width=True):
                result = st.session_state.run_result or run_user_code(st.session_state.user_code, manual_input)

                feedback = analyze_code_error(
                    problem_text=st.session_state.problem_text,
                    user_code=st.session_state.user_code,
                    error_text=result.get("stderr", ""),
                    run_output=result.get("stdout", ""),
                    expected_output=expected_output,
                )
                st.session_state.ai_feedback = feedback

        if st.session_state.run_result:
            result = st.session_state.run_result

            with st.expander("Kết quả chạy code", expanded=True):
                st.write(f"**Return code:** {result.get('returncode')}")
                st.write("**Output:**")
                st.code(result.get("stdout", "") or "(khong co output)", language="text")

                if result.get("stderr"):
                    st.write("**Lỗi:**")
                    st.code(result.get("stderr", ""), language="text")

                if expected_output:
                    st.write("**Output mong đợi:**")
                    st.code(expected_output, language="text")

        if st.session_state.ai_feedback:
            with st.expander("Gợi ý sửa từ AI", expanded=True):
                st.write(st.session_state.ai_feedback)

        st.divider()
        st.subheader("4) Lưu file")

        custom_name = st.text_input(
            "Đặt tên file",
            placeholder="Ví dụ: 2.2, bai_1, tong_2_so",
        )

        st.markdown(
            f'<div class="file-preview">Tên file sẽ là: <b>{preview_file_name(custom_name)}</b>.py / .md / .json</div>',
            unsafe_allow_html=True,
        )

        save_payload = {
            "title": lesson.get("title", "Python Practice"),
            "summary": lesson.get("summary", ""),
            "explanation_easy": lesson.get("explanation_easy", ""),
            "notes": lesson.get("notes", []),
            "starter_code": lesson.get("starter_code", ""),
            "user_code": st.session_state.user_code,
        }

        py_path, md_path, json_path = save_outputs(save_payload, str(OUTPUT_DIR), custom_name)

        dl1, dl2, dl3 = st.columns(3)

        with dl1:
            with open(py_path, "rb") as f:
                st.download_button(
                    "Tải .py",
                    f,
                    file_name=os.path.basename(py_path),
                    use_container_width=True,
                    key="download_py",
                )

        with dl2:
            with open(md_path, "rb") as f:
                st.download_button(
                    "Tải .md",
                    f,
                    file_name=os.path.basename(md_path),
                    use_container_width=True,
                    key="download_md",
                )

        with dl3:
            with open(json_path, "rb") as f:
                st.download_button(
                    "Tải .json",
                    f,
                    file_name=os.path.basename(json_path),
                    use_container_width=True,
                    key="download_json",
                )
    else:
        st.info("Sau khi bạn bấm 'Tạo gợi ý học tập', khu học và viết code sẽ hiện ở đây.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("5) Xuất ZIP project")

if st.button("📦 Tạo file ZIP project", use_container_width=True):
    try:
        zip_path = zip_project(PROJECT_DIR, EXPORT_DIR)
        st.session_state.zip_path = zip_path
        st.success("Đã tạo file ZIP project.")
    except Exception as e:
        st.error(f"Lỗi tạo ZIP: {e}")

if st.session_state.zip_path and os.path.exists(st.session_state.zip_path):
    with open(st.session_state.zip_path, "rb") as f:
        st.download_button(
            "⬇️ Tải file ZIP project",
            f,
            file_name="python_study_assistant_export.zip",
            use_container_width=True,
        )
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("6) Commit và Push lên GitHub")
st.caption("Chỉ thực hiện sau khi bạn đã tự xem lại nội dung.")

git_col_1, git_col_2 = st.columns(2)
with git_col_1:
    remote_url = st.text_input(
        "GitHub remote URL",
        placeholder="https://github.com/ban/project-cua-toi.git",
    )
with git_col_2:
    commit_message = st.text_input(
        "Commit message",
        value="Add reviewed Python exercise solution",
    )

review_ok_manual = st.checkbox("Tôi đã tự xem lại nội dung trước khi commit/push")
push_btn = st.button("🚀 Commit và Push", use_container_width=True)

if push_btn:
    if not has_git():
        st.error("Máy của bạn chưa cài Git hoặc Git chưa có trong PATH.")
    elif not review_ok_manual:
        st.error("Bạn cần xác nhận đã tự review nội dung trước khi push.")
    elif not remote_url.strip():
        st.error("Bạn cần nhập GitHub remote URL.")
    else:
        logs = []

        ok, msg = init_repo_if_needed(str(PROJECT_DIR))
        logs.append(msg)

        if ok:
            ok, msg = set_remote(str(PROJECT_DIR), remote_url.strip())
            logs.append(msg)

        if ok:
            ok, msg = commit_all(str(PROJECT_DIR), commit_message.strip() or "Update project")
            logs.append(msg)

        if ok:
            ok, msg = push(str(PROJECT_DIR), branch="main")
            logs.append(msg)

        if ok:
            st.success("Đã commit và push thành công.")
        else:
            st.error("Push chưa thành công. Xem log bên dưới để sửa.")

        st.code("\n\n".join(logs), language="bash")

with st.expander("Hướng dẫn nhập API key"):
    st.code(
        "Windows PowerShell:\n$env:OPENROUTER_API_KEY='API_MOI_CUA_BAN'\npython -m streamlit run app.py\n\n"
        "Windows CMD:\nset OPENROUTER_API_KEY=API_MOI_CUA_BAN\npython -m streamlit run app.py",
        language="bash",
    )
st.markdown("</div>", unsafe_allow_html=True)