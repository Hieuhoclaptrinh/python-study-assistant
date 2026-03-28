import os
import shutil
import tempfile
from pathlib import Path

import streamlit as st

from ai_solver import save_outputs, solve_problem, transcribe_from_image, transcribe_problem_text
from github_utils import commit_ai_outputs, commit_all, has_git, init_repo_if_needed, push, set_remote

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
.main {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
h1, h2, h3, p, label, div, span {
    color: #eef2ff;
}
.hero-card, .glass {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid rgba(99, 102, 241, 0.28);
    border-radius: 22px;
    padding: 1rem 1.1rem;
    box-shadow: 0 18px 50px rgba(0,0,0,0.22);
}
.badge {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.16);
    color: #bfdbfe;
    border: 1px solid rgba(96, 165, 250, 0.32);
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
}
.note {
    border-left: 4px solid #60a5fa;
    background: rgba(30, 41, 59, 0.72);
    padding: 0.8rem 1rem;
    border-radius: 12px;
    color: #dbeafe;
}
textarea, input {
    color: #0f172a !important;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

if "solution" not in st.session_state:
    st.session_state.solution = None
if "problem_text" not in st.session_state:
    st.session_state.problem_text = ""
if "zip_path" not in st.session_state:
    st.session_state.zip_path = None


def zip_project(project_dir: Path, export_dir: Path) -> str:
    zip_base = export_dir / "python_study_assistant_export"
    if zip_base.with_suffix(".zip").exists():
        zip_base.with_suffix(".zip").unlink()

    shutil.make_archive(str(zip_base), "zip", root_dir=str(project_dir), base_dir=".")
    return str(zip_base.with_suffix(".zip"))


with st.container():
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    cols = st.columns([1.15, 1])
    with cols[0]:
        st.title("🐍 Python Study Assistant")
        st.write(
            "Nhận đề bài bằng ảnh hoặc văn bản, trích nội dung, sinh code Python có giải thích, "
            "rồi để bạn tự kiểm tra trước khi commit và push lên GitHub."
        )
        st.markdown(
            '<span class="badge">Ảnh đề bài</span>'
            '<span class="badge">Giải thích từng bước</span>'
            '<span class="badge">Xuất file .py</span>'
            '<span class="badge">Push GitHub thủ công</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="note"><b>Lưu ý:</b> App này hỗ trợ học tập và review. Không có chế độ tự động nộp bài không qua xác nhận của bạn.</div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        if ASSET_BANNER.exists():
            st.image(str(ASSET_BANNER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("1) Nhập đề bài")
    input_mode = st.radio("Chọn cách đưa đề bài", ["Nhập văn bản", "Tải ảnh đề bài"], horizontal=True)

    if input_mode == "Nhập văn bản":
        problem_text = st.text_area(
            "Dán đề bài Python",
            value=st.session_state.problem_text,
            height=220,
            placeholder="Ví dụ: Nhập vào 2 số nguyên, tính tổng và in ra màn hình...",
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
        height=220,
        disabled=False,
        key="preview_problem_text",
    )

    extra_request = st.text_input(
        "Yêu cầu thêm",
        placeholder="Ví dụ: dùng input(), chỉ dùng if/else, code cho người mới học",
    )

    if st.button("✨ Sinh lời giải và code Python", type="primary", use_container_width=True):
        if not st.session_state.problem_text.strip():
            st.error("Bạn cần nhập đề bài hoặc trích đề từ ảnh trước.")
        else:
            try:
                with st.spinner("AI đang phân tích đề bài..."):
                    st.session_state.solution = solve_problem(st.session_state.problem_text, extra_request)
                st.success("Đã sinh lời giải và code.")
            except Exception as e:
                st.error(f"Lỗi sinh lời giải: {e}")

with right:
    st.subheader("2) Kết quả")

    if st.session_state.solution:
        solution = st.session_state.solution

        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(f"### {solution.get('title', 'Python Solution')}")
        st.write(solution.get("summary", ""))

        with st.expander("Giải thích cách làm", expanded=True):
            st.write(solution.get("explanation", ""))

        with st.expander("Code Python", expanded=True):
            st.code(solution.get("code", "") or "", language="python")

        with st.expander("Ví dụ chạy"):
            st.write(solution.get("sample_run", ""))

        notes = solution.get("notes", [])
        if notes:
            st.write("**Ghi chú:**")
            for note in notes:
                st.write(f"- {note}")

        st.markdown("</div>", unsafe_allow_html=True)

        py_path, md_path, json_path = save_outputs(solution, str(OUTPUT_DIR))

        with open(py_path, "rb") as f:
            st.download_button(
                "Tải file solution.py",
                f,
                file_name=os.path.basename(py_path),
                use_container_width=True,
                key="download_solution_py",
            )

        with open(md_path, "rb") as f:
            st.download_button(
                "Tải file solution.md",
                f,
                file_name=os.path.basename(md_path),
                use_container_width=True,
                key="download_solution_md",
            )

        with open(json_path, "rb") as f:
            st.download_button(
                "Tải file solution.json",
                f,
                file_name=os.path.basename(json_path),
                use_container_width=True,
                key="download_solution_json",
            )

        st.divider()
        st.subheader("3) Lưu kết quả AI lên GitHub")
        st.caption("Chỉ push file kết quả sau khi bạn đã tự xem lại nội dung.")

        review_ok_after_ai = st.checkbox(
            "Tôi đã tự xem lại nội dung và muốn lưu file kết quả AI này lên GitHub",
            key="review_ok_after_ai",
        )

        auto_commit_message = solution.get("title", "Add AI reviewed solution")

        push_after_review = st.button(
            "🚀 Commit và Push file kết quả AI",
            use_container_width=True,
            key="push_after_review_btn",
        )

        if push_after_review:
            if not has_git():
                st.error("Máy của bạn chưa cài Git hoặc Git chưa có trong PATH.")
            elif not review_ok_after_ai:
                st.error("Bạn cần xác nhận đã tự xem lại nội dung trước khi push.")
            else:
                logs = []

                ok, msg = init_repo_if_needed(str(PROJECT_DIR))
                logs.append(msg)

                if ok:
                    ok, msg = commit_ai_outputs(
                        str(PROJECT_DIR),
                        auto_commit_message,
                    )
                    logs.append(msg)

                if ok:
                    ok, msg = push(str(PROJECT_DIR), branch="main")
                    logs.append(msg)

                if ok:
                    st.success("Đã lưu file kết quả AI và push lên GitHub thành công.")
                else:
                    st.error("Push chưa thành công. Xem log bên dưới để sửa.")

                st.code("\n\n".join(logs), language="bash")
    else:
        st.info("Kết quả sẽ hiện ở đây sau khi bạn bấm nút sinh lời giải.")

st.divider()
st.subheader("3) Xuất ZIP project")

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

st.divider()
st.subheader("4) Commit và Push lên GitHub")
st.caption("Chỉ thực hiện sau khi bạn đã tự xem lại nội dung.")

col1, col2 = st.columns(2)
with col1:
    remote_url = st.text_input(
        "GitHub remote URL",
        placeholder="https://github.com/ban/project-cua-toi.git",
    )
with col2:
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
        'Mở file ai_solver.py và thay:\nOPENROUTER_API_KEY = "API_MOI_CUA_BAN"',
        language="python",
    )