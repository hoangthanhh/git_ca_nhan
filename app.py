from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json

HOST = "0.0.0.0"
PORT = 8889

HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Thống kê sinh viên trong lớp</title>
  <style>
    :root {
      --ink: #18212f;
      --muted: #667085;
      --line: #d9e1ea;
      --surface: #ffffff;
      --background: #f4f7fb;
      --male: #247ba0;
      --female: #e76f51;
      --accent: #16324f;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 90% 0%, #dceef5 0, transparent 28rem),
        linear-gradient(135deg, #f9fbfd 0%, var(--background) 100%);
      font-family: Georgia, "Times New Roman", serif;
    }

    .page {
      width: min(100% - 32px, 980px);
      margin: 0 auto;
      padding: 58px 0 70px;
    }

    .eyebrow {
      margin: 0 0 14px;
      color: var(--male);
      font-family: Arial, sans-serif;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    h1 {
      max-width: 680px;
      margin: 0;
      font-size: clamp(2.3rem, 6vw, 4.8rem);
      line-height: 0.98;
      letter-spacing: -0.04em;
    }

    .intro {
      max-width: 600px;
      margin: 20px 0 42px;
      color: var(--muted);
      font-family: Arial, sans-serif;
      font-size: 1rem;
      line-height: 1.6;
    }

    .layout {
      display: grid;
      grid-template-columns: minmax(230px, 0.75fr) minmax(0, 1.25fr);
      gap: 22px;
      align-items: stretch;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: 0 18px 45px rgba(22, 50, 79, 0.08);
    }

    .form-panel { padding: 28px; }
    .chart-panel { padding: 28px 30px 30px; }

    h2 {
      margin: 0 0 24px;
      font-size: 1.45rem;
      letter-spacing: -0.02em;
    }

    label {
      display: block;
      margin: 19px 0 8px;
      color: var(--muted);
      font-family: Arial, sans-serif;
      font-size: 0.86rem;
      font-weight: 700;
    }

    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 5px;
      padding: 13px 14px;
      color: var(--ink);
      background: #fbfcfe;
      font: 1rem Arial, sans-serif;
      outline: none;
    }

    input:focus {
      border-color: var(--male);
      box-shadow: 0 0 0 3px rgba(36, 123, 160, 0.14);
    }

    button {
      width: 100%;
      margin-top: 26px;
      border: 0;
      border-radius: 5px;
      padding: 14px 18px;
      color: white;
      background: var(--accent);
      cursor: pointer;
      font: 700 0.9rem Arial, sans-serif;
      transition: background 160ms ease, transform 160ms ease;
    }

    button:hover { background: var(--male); transform: translateY(-1px); }
    button:active { transform: translateY(0); }

    .error {
      min-height: 20px;
      margin: 13px 0 0;
      color: #b42318;
      font: 0.83rem Arial, sans-serif;
    }

    .summary {
      display: flex;
      gap: 22px;
      margin: -5px 0 30px;
      color: var(--muted);
      font: 0.82rem Arial, sans-serif;
    }

    .summary strong {
      display: block;
      margin-top: 4px;
      color: var(--ink);
      font: 700 1.65rem Georgia, serif;
    }

    .chart {
      display: grid;
      grid-template-columns: repeat(2, minmax(90px, 1fr));
      gap: 34px;
      align-items: end;
      min-height: 310px;
      padding: 22px 22px 0;
      border-bottom: 1px solid var(--line);
      background: repeating-linear-gradient(
        to top,
        transparent 0,
        transparent 61px,
        rgba(217, 225, 234, 0.55) 62px
      );
    }

    .bar-group {
      display: flex;
      height: 285px;
      flex-direction: column;
      justify-content: end;
      align-items: center;
      gap: 12px;
    }

    .bar-value {
      color: var(--ink);
      font: 700 1.25rem Arial, sans-serif;
    }

    .bar {
      width: min(92px, 65%);
      min-height: 8px;
      border-radius: 5px 5px 0 0;
      transition: height 450ms cubic-bezier(.2,.8,.2,1);
    }

    .bar.male { background: var(--male); }
    .bar.female { background: var(--female); }

    .bar-label {
      color: var(--muted);
      font: 700 0.83rem Arial, sans-serif;
      text-align: center;
    }

    .legend {
      display: flex;
      gap: 22px;
      margin-top: 19px;
      color: var(--muted);
      font: 0.82rem Arial, sans-serif;
    }

    .legend span { display: inline-flex; align-items: center; gap: 8px; }
    .legend i { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    .legend .male-dot { background: var(--male); }
    .legend .female-dot { background: var(--female); }

    @media (max-width: 680px) {
      .page { padding-top: 38px; }
      .layout { grid-template-columns: 1fr; }
      h1 { font-size: 3.1rem; }
      .chart { min-height: 270px; }
    }
  </style>
</head>
<body>
  <main class="page">
    <p class="eyebrow">Bảng thống kê lớp học</p>
    <h1>Số sinh viên nam và nữ</h1>
    <p class="intro">Nhập số lượng sinh viên trong lớp để xem nhanh sự phân bố theo giới tính.</p>

    <section class="layout">
      <form class="panel form-panel" id="student-form">
        <h2>Nhập dữ liệu</h2>
        <label for="male">Số sinh viên nam</label>
        <input id="male" name="male" type="number" min="0" step="1" value="18" required>
        <label for="female">Số sinh viên nữ</label>
        <input id="female" name="female" type="number" min="0" step="1" value="22" required>
        <p class="error" id="error" role="alert"></p>
        <button type="submit">Cập nhật biểu đồ</button>
      </form>

      <section class="panel chart-panel" aria-labelledby="chart-title">
        <h2 id="chart-title">Biểu đồ cột</h2>
        <div class="summary">
          <div>Tổng số<strong id="total">40</strong></div>
          <div>Tỷ lệ nữ<strong id="female-percent">55%</strong></div>
        </div>
        <div class="chart" aria-label="Biểu đồ số sinh viên nam và nữ">
          <div class="bar-group">
            <div class="bar-value" id="male-value">18</div>
            <div class="bar male" id="male-bar" style="height: 45%"></div>
            <div class="bar-label">Nam</div>
          </div>
          <div class="bar-group">
            <div class="bar-value" id="female-value">22</div>
            <div class="bar female" id="female-bar" style="height: 55%"></div>
            <div class="bar-label">Nữ</div>
          </div>
        </div>
        <div class="legend">
          <span><i class="male-dot"></i>Nam</span>
          <span><i class="female-dot"></i>Nữ</span>
        </div>
      </section>
    </section>
  </main>

  <script>
    const form = document.getElementById("student-form");
    const error = document.getElementById("error");
    const maleInput = document.getElementById("male");
    const femaleInput = document.getElementById("female");

    function renderChart(male, female) {
      const total = male + female;
      const max = Math.max(male, female, 1);
      document.getElementById("male-value").textContent = male;
      document.getElementById("female-value").textContent = female;
      document.getElementById("total").textContent = total;
      document.getElementById("female-percent").textContent = total ? `${Math.round(female / total * 100)}%` : "0%";
      document.getElementById("male-bar").style.height = `${male / max * 78 + 8}%`;
      document.getElementById("female-bar").style.height = `${female / max * 78 + 8}%`;
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      error.textContent = "";
      const male = Number(maleInput.value);
      const female = Number(femaleInput.value);

      if (!Number.isInteger(male) || !Number.isInteger(female) || male < 0 || female < 0) {
        error.textContent = "Vui lòng nhập số nguyên không âm.";
        return;
      }

      try {
        const response = await fetch("/api/chart", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ male, female })
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "Không thể cập nhật dữ liệu.");
        renderChart(result.male, result.female);
      } catch (requestError) {
        error.textContent = requestError.message;
      }
    });
  </script>
</body>
</html>"""


class AppHandler(BaseHTTPRequestHandler):
    def send_content(self, content, content_type="text/html; charset=utf-8", status=200):
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_content(HTML)
        else:
            self.send_content("Không tìm thấy trang.", status=404)

    def do_POST(self):
        if self.path != "/api/chart":
            self.send_content(json.dumps({"error": "Không tìm thấy đường dẫn."}), "application/json", 404)
            return

        length = int(self.headers.get("Content-Length", 0))
        form_data = parse_qs(self.rfile.read(length).decode("utf-8"))
        try:
            male = int(form_data.get("male", [""])[0])
            female = int(form_data.get("female", [""])[0])
            if male < 0 or female < 0:
                raise ValueError
        except ValueError:
            self.send_content(json.dumps({"error": "Số sinh viên phải là số nguyên không âm."}), "application/json", 400)
            return

        self.send_content(json.dumps({"male": male, "female": female}), "application/json")

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string}] {format_string % args}")


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), AppHandler)
    print(f"Ứng dụng đang chạy tại http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng ứng dụng.")
    finally:
        server.server_close()
