import os
import json
import base64
import re
import subprocess
import sys
import tempfile
from openai import OpenAI

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

CHAT_MODEL = "openai/gpt-4o-mini"
VISION_MODEL = "openai/gpt-4o-mini"


def _client():
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Chua co OPENROUTER_API_KEY trong bien moi truong.")
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )


def _safe_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()
    return str(value).strip()


def _extract_message_content(response):
    try:
        msg = response.choices[0].message
    except Exception:
        return ""

    content = getattr(msg, "content", None)
    text = _safe_text(content)
    if text:
        return text

    for attr in ["reasoning", "refusal"]:
        value = getattr(msg, attr, None)
        text = _safe_text(value)
        if text:
            return text

    return ""


def _strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_+-]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _extract_json_object(text):
    text = _strip_code_fences(text)

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("Khong tim duoc JSON hop le trong phan hoi model.")


def _to_list(value):
    if isinstance(value, list):
        return [str(x) for x in value]
    if value:
        return [str(value)]
    return []


def _normalize_lesson(data):
    if not isinstance(data, dict):
        data = {}

    starter_code = data.get("starter_code") or ""

    if isinstance(starter_code, dict):
        first_key = next(iter(starter_code.keys()), "")
        starter_code = str(starter_code.get(first_key, ""))
    elif isinstance(starter_code, list):
        starter_code = "\n".join(str(x) for x in starter_code)
    else:
        starter_code = str(starter_code)

    return {
        "title": str(data.get("title") or "Huong dan giai bai Python"),
        "summary": str(data.get("summary") or ""),
        "explanation_easy": str(data.get("explanation_easy") or ""),
        "hint_level_1": _to_list(data.get("hint_level_1")),
        "hint_level_2": _to_list(data.get("hint_level_2")),
        "starter_code": starter_code.strip(),
        "sample_tests": data.get("sample_tests") if isinstance(data.get("sample_tests"), list) else [],
        "notes": _to_list(data.get("notes")),
    }


def generate_learning_plan(problem_text, extra_request=""):
    client = _client()

    problem_text = _safe_text(problem_text)
    extra_request = _safe_text(extra_request)

    if not problem_text:
        return {
            "title": "Loi",
            "summary": "De bai rong.",
            "explanation_easy": "Ban chua nhap noi dung de bai.",
            "hint_level_1": ["Hay nhap noi dung de bai truoc."],
            "hint_level_2": [],
            "starter_code": "# TODO: viet code cua ban o day\n",
            "sample_tests": [],
            "notes": [],
        }

    prompt = f"""
Ban la tro giang Python cho nguoi moi hoc.

NHIEM VU:
- Doc de bai nguoi dung gui.
- Neu de co nhieu bai, chi lay 1 bai dau tien de huong dan.
- Khong tra ve nhieu bai cung luc.
- Khong tra ve loi giai day du.
- Chi dua ra huong dan de hoc va code khung de hoc sinh tu dien.
- Giai thich bang tieng Viet de hieu, cau ngan, don gian.
- Truong "starter_code" phai la 1 doan code Python dang chuoi.
- "starter_code" KHONG duoc la dict.
- "starter_code" KHONG duoc la list.
- Trong code khung duoc dung TODO hoac pass.
- Khong dua dap an hoan chinh.
- Chi tra ve JSON hop le.

DE BAI:
{problem_text}

YEU CAU THEM:
{extra_request}

JSON mau:
{{
  "title": "Ten bai",
  "summary": "Tom tat bai toan ngan gon",
  "explanation_easy": "Giai thich de hieu cho nguoi moi",
  "hint_level_1": ["goi y 1", "goi y 2"],
  "hint_level_2": ["goi y gan hon 1", "goi y gan hon 2"],
  "starter_code": "mot doan code Python khung co TODO, khong phai dap an day du",
  "sample_tests": [
    {{"input": "2\\n3", "output": "5"}}
  ],
  "notes": ["luu y 1", "luu y 2"]
}}
""".strip()

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Ban la tro giang Python, uu tien day hoc, chi dua goi y va code khung, khong dua dap an day du.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1800,
    )

    content = _extract_message_content(response)
    if not content:
        raise ValueError("Model khong tra ve noi dung.")

    data = _extract_json_object(content)
    result = _normalize_lesson(data)

    if not result["starter_code"].strip():
        result["starter_code"] = "# TODO: viet code cua ban o day\n"

    return result


def analyze_code_error(problem_text, user_code, error_text="", run_output="", expected_output=""):
    client = _client()

    prompt = f"""
Ban la giao vien Python cho nguoi moi hoc.

DE BAI:
{problem_text}

CODE CUA HOC SINH:
{user_code}

LOI KHI CHAY:
{error_text}

KET QUA THUC TE:
{run_output}

KET QUA MONG DOI:
{expected_output}

YEU CAU:
- Chi ra hoc sinh sai o dau.
- Giai thich bang tieng Viet de hieu.
- Neu co the, noi dong nao can sua.
- Khong viet lai toan bo bai.
- Khong dua dap an day du.
- Chi dua goi y sua tung buoc.
- Tra ve van ban ngan gon, ro rang.
""".strip()

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Ban la giao vien Python, chi goi y sua loi, khong viet dap an day du.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )

    return _extract_message_content(response) or "Chua phan tich duoc loi."


def run_user_code(user_code, stdin_data=""):
    user_code = _safe_text(user_code)

    if not user_code:
        return {
            "ok": False,
            "stdout": "",
            "stderr": "Ban chua nhap code.",
            "returncode": -1,
        }

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(user_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            input=stdin_data,
            text=True,
            capture_output=True,
            timeout=8,
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "stdout": "",
            "stderr": "Code chay qua lau, co the bi lap vo han.",
            "returncode": -1,
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def transcribe_problem_text(text):
    return _safe_text(text)


def _image_to_data_url(image_path: str) -> str:
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png"

    if ext in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif ext == ".webp":
        mime = "image/webp"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def transcribe_from_image(image_path):
    client = _client()
    image_data_url = _image_to_data_url(image_path)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Hay doc va chep lai chinh xac noi dung de bai trong anh. Chi tra ve van ban thuan.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Hay OCR anh nay."},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
        temperature=0,
        max_tokens=1200,
    )

    content = _extract_message_content(response)
    return content or ""


def save_outputs(solution, output_dir, custom_name=None):
    os.makedirs(output_dir, exist_ok=True)

    if custom_name:
        custom_name = custom_name.replace(".", "_")
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", custom_name).strip("_").lower()
    else:
        title = solution.get("title") or "solution"
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_").lower()

    if not safe_name:
        safe_name = "solution"

    py_path = os.path.join(output_dir, f"{safe_name}.py")
    md_path = os.path.join(output_dir, f"{safe_name}.md")
    json_path = os.path.join(output_dir, f"{safe_name}.json")

    code = solution.get("user_code") or solution.get("starter_code") or ""
    summary = solution.get("summary") or ""
    explanation = solution.get("explanation_easy") or ""
    notes = solution.get("notes") or []

    with open(py_path, "w", encoding="utf-8") as f:
        f.write(str(code))

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {solution.get('title', 'Solution')}\n\n")
        f.write("## Tom tat\n\n")
        f.write(str(summary) + "\n\n")
        f.write("## Giai thich de hieu\n\n")
        f.write(str(explanation) + "\n\n")

        if notes:
            f.write("## Ghi chu\n\n")
            for note in notes:
                f.write(f"- {note}\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(solution, f, ensure_ascii=False, indent=2)

    return py_path, md_path, json_path