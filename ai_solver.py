import os
import json
import base64
import re
from openai import OpenAI

# NEN DUNG BIEN MOI TRUONG:
# Windows CMD:
#   set OPENROUTER_API_KEY=key_moi
# PowerShell:
#   $env:OPENROUTER_API_KEY="key_moi"
OPENROUTER_API_KEY = "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"

# Dat model ban dang co tren OpenRouter.
# Khong nen de "openrouter/free" vi de loi/khong on dinh.
CHAT_MODEL = "openai/gpt-4o-mini"
VISION_MODEL = "openai/gpt-4o-mini"

def _client():
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "Chua co OPENROUTER_API_KEY. Hay set bien moi truong OPENROUTER_API_KEY."
        )

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

    # Du phong cho mot so truong hop co reasoning/field la
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

    # Thu parse truc tiep
    try:
        return json.loads(text)
    except Exception:
        pass

    # Tim block JSON dau tien
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("Khong tim duoc JSON hop le trong phan hoi model.")


def _normalize_solution(data):
    if not isinstance(data, dict):
        data = {}

    notes = data.get("notes", [])
    if not isinstance(notes, list):
        notes = [str(notes)]

    return {
        "title": str(data.get("title") or "Giai bai tap Python"),
        "summary": str(data.get("summary") or ""),
        "explanation": str(data.get("explanation") or ""),
        "code": str(data.get("code") or ""),
        "sample_run": str(data.get("sample_run") or ""),
        "notes": [str(x) for x in notes],
    }


def solve_problem(problem_text, extra_request=""):
    client = _client()

    problem_text = _safe_text(problem_text)
    extra_request = _safe_text(extra_request)

    if not problem_text:
        return {
            "title": "Loi",
            "summary": "De bai rong.",
            "explanation": "Ban chua nhap noi dung de bai.",
            "code": "",
            "sample_run": "",
            "notes": ["Hay nhap de bai truoc khi giai."],
        }

    prompt = f"""
Ban la tro ly hoc Python.

NHIEM VU:
- Doc de bai nguoi dung gui.
- Neu de gom nhieu bai (vi du Bai 1, Bai 2, Bai 3...), hay giai TAT CA.
- Viet loi giai de hieu cho nguoi moi hoc.
- Tao code Python chay duoc.
- Neu de gom nhieu bai, hay tao 1 file code gom day du cac bai va co comment phan tach tung bai.
- Neu co phep chia, nho tranh loi chia cho 0.
- Neu de bai co noi dung mo ho, hay dua ra cach giai hop ly nhat.

DE BAI:
{problem_text}

YEU CAU THEM:
{extra_request}

BAT BUOC:
- Chi tra ve JSON hop le.
- Khong them markdown.
- Khong them giai thich ngoai JSON.
- Truong "code" phai la chuoi code Python hop le.

JSON dung mau nay:
{{
  "title": "Giai bai tap Python",
  "summary": "Tom tat ngan gon ve cac bai",
  "explanation": "Giai thich chi tiet",
  "code": "print('hello')",
  "sample_run": "Vi du chay",
  "notes": ["ghi chu 1", "ghi chu 2"]
}}
""".strip()

    last_error = None
    last_content = ""

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Ban la tro ly Python than thien, ro rang, uu tien JSON hop le.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1800,
            )

            content = _extract_message_content(response)
            last_content = content

            if not content:
                raise ValueError("Model khong tra ve noi dung.")

            data = _extract_json_object(content)
            result = _normalize_solution(data)

            # Neu model tra code rong, dung fallback
            if not result["code"].strip():
                result["code"] = (
                    "# Model khong tra ve code hop le\n"
                    "# Hay thu lai voi model khac tren OpenRouter\n"
                )
                result["notes"].append("Model tra ve JSON nhung truong code dang rong.")

            return result

        except Exception as e:
            last_error = e

    return {
        "title": "Khong parse duoc loi giai",
        "summary": "Model khong tra ve JSON dung dinh dang.",
        "explanation": (
            f"Loi: {last_error}\n\n"
            f"Noi dung thuc te model tra ve:\n{last_content}"
        ),
        "code": last_content or "# Khong lay duoc noi dung tra ve tu model",
        "sample_run": "",
        "notes": [
            "Hay doi model khac trong OpenRouter.",
            "Khong nen dung model alias qua chung chung.",
            "Kiem tra model co ho tro chat/vision hay khong.",
        ],
    }


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
                "content": (
                    "Hay doc va chep lai chinh xac noi dung de bai trong anh. "
                    "Chi tra ve van ban thuan, khong markdown."
                ),
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


def save_outputs(solution, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    title = solution.get("title") or "solution"
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_").lower() or "solution"

    py_path = os.path.join(output_dir, f"{safe_name}.py")
    md_path = os.path.join(output_dir, f"{safe_name}.md")
    json_path = os.path.join(output_dir, f"{safe_name}.json")

    code = solution.get("code") or ""
    summary = solution.get("summary") or ""
    explanation = solution.get("explanation") or ""
    sample_run = solution.get("sample_run") or ""
    notes = solution.get("notes") or []

    with open(py_path, "w", encoding="utf-8") as f:
        f.write(str(code))

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {solution.get('title', 'Solution')}\n\n")
        f.write("## Tom tat\n\n")
        f.write(str(summary) + "\n\n")
        f.write("## Giai thich\n\n")
        f.write(str(explanation) + "\n\n")

        if sample_run:
            f.write("## Vi du chay\n\n")
            f.write(str(sample_run) + "\n\n")

        if notes:
            f.write("## Ghi chu\n\n")
            for note in notes:
                f.write(f"- {note}\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(solution, f, ensure_ascii=False, indent=2)

    return py_path, md_path, json_path


if __name__ == "__main__":
    # Test nhanh
    sample_problem = """
2.3. Luyen tap

Bai 1:
Nhap vao tu ban phim hai so nguyen. Tinh tong va in ra tong cua hai so nguyen do.

Bai 2:
Nhap vao tu ban phim chuoi ky tu, in ra chuoi ky tu do.

Bai 3:
Nhap vao tu ban phim ba so nguyen. Tinh toan va in ra man hinh:
a) Tong va tich cua ba so do
b) Hieu cua 2 so bat ky trong 3 so do
c) Phep chia lay phan nguyen, phan du va ket qua chinh xac cua 2 so bat ky trong 3 so do

Bai 4:
Nhap vao tu ban phim ba chuoi ky tu. In ra man hinh mot chuoi ky tu duoc ghep tu ba chuoi nhap vao.

Bai 5:
Tinh toan va in ra Chu vi, dien tich cua hinh tron.
"""

    result = solve_problem(sample_problem)
    print(json.dumps(result, ensure_ascii=False, indent=2))