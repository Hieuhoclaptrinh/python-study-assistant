<<<<<<< HEAD
# Python Study Assistant

App Streamlit hỗ trợ học Python:
- nhập đề bằng văn bản hoặc ảnh
- AI trích nội dung từ ảnh
- AI giải thích cách làm và sinh code Python
- xuất `solution.py` và `solution.md`
- commit / push lên GitHub sau khi bạn tự kiểm tra lại

## Cài đặt

```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Biến môi trường

Thiết lập ít nhất một trong hai kiểu:

### OpenAI
```bash
OPENAI_API_KEY=...
```

### OpenRouter
```bash
OPENROUTER_API_KEY=...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

## Lưu ý

- App này được thiết kế cho mục đích học tập và review.
- Bạn nên tự đọc lại code trước khi commit/push.
- Không nên hard-code API key trong file Python.
=======
# python-study-assistant
>>>>>>> 4ce5dfda10ee3dc14443ee63b42dc9a048a2fcf9
