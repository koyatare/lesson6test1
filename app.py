# -*- coding: utf-8 -*-
"""
BMI計算機（標準ライブラリのみ / Render対応）
- 外部ライブラリ不使用（http.server + wsgiref のみ）
- ローカル・Render本番どちらも同じコードで動作
- Start: python app.py
"""

import os
from wsgiref.simple_server import make_server


def calc_bmi(height_cm, weight_kg):
    """
    身長(cm)と体重(kg)からBMIと判定区分を計算する。

    引数:
        height_cm (float): 身長（センチメートル）。例: 170.0
        weight_kg (float): 体重（キログラム）。例: 65.0

    戻り値:
        tuple(float, str): (BMI値を小数第1位で丸めた値, 判定文字列)
        計算できない場合（0以下や不正値）は (0.0, "計算不可") を返す。

    例:
        calc_bmi(170, 65) -> (22.5, "標準")
    """
    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)
        if height_cm <= 0 or weight_kg <= 0:
            return 0.0, "計算不可"
    except (TypeError, ValueError):
        # 数値に変換できない入力は例外時0扱いとする簡易ハンドリング
        return 0.0, "計算不可"

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 1)

    if bmi < 18.5:
        judge = "低体重（やせ）"
    elif bmi < 25:
        judge = "標準（普通）"
    elif bmi < 30:
        judge = "肥満（1度）"
    elif bmi < 35:
        judge = "肥満（2度）"
    elif bmi < 40:
        judge = "肥満（3度）"
    else:
        judge = "肥満（4度）"

    return bmi, judge


def render_page(height_val="", weight_val="", result_html=""):
    """
    HTMLページ全体を組み立てる。

    引数:
        height_val (str): フォームに再表示する身長の入力値。例: "170"
        weight_val (str): フォームに再表示する体重の入力値。例: "65"
        result_html (str): 結果表示エリアに挿入するHTML文字列。例: "<p>BMI: 22.5（標準）</p>"

    戻り値:
        str: 完成したHTMLドキュメント全体
    """
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BMI計算機</title>
<style>
  body {{
    font-family: "Hiragino Sans", "Meiryo", sans-serif;
    background-color: #f4f6f8;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    min-height: 100vh;
  }}
  .container {{
    background: #ffffff;
    margin-top: 40px;
    padding: 32px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    width: 90%;
    max-width: 420px;
    height: fit-content;
  }}
  h1 {{
    font-size: 22px;
    text-align: center;
    color: #2c3e50;
    margin-bottom: 24px;
  }}
  label {{
    display: block;
    font-size: 14px;
    color: #555;
    margin-bottom: 6px;
  }}
  input[type="number"] {{
    width: 100%;
    padding: 10px;
    margin-bottom: 16px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 16px;
    box-sizing: border-box;
  }}
  .btn-row {{
    display: flex;
    gap: 10px;
    margin-top: 8px;
  }}
  button {{
    flex: 1;
    padding: 12px;
    font-size: 15px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }}
  .btn-calc {{
    background-color: #2c7be5;
    color: #fff;
  }}
  .btn-calc:hover {{
    background-color: #1a64c4;
  }}
  .btn-clear {{
    background-color: #e9ecef;
    color: #333;
  }}
  .btn-clear:hover {{
    background-color: #d6d9dc;
  }}
  .result {{
    margin-top: 22px;
    padding: 16px;
    background-color: #eef6ff;
    border-radius: 8px;
    text-align: center;
  }}
  .result .bmi-value {{
    font-size: 28px;
    font-weight: bold;
    color: #2c3e50;
  }}
  .result .judge {{
    font-size: 16px;
    color: #2c7be5;
    margin-top: 6px;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>BMI計算機</h1>
  <form method="POST" action="/">
    <label for="height">身長（cm）</label>
    <input type="number" step="0.1" id="height" name="height" value="{height_val}" placeholder="例: 170">

    <label for="weight">体重（kg）</label>
    <input type="number" step="0.1" id="weight" name="weight" value="{weight_val}" placeholder="例: 65">

    <div class="btn-row">
      <button type="submit" class="btn-calc">計算する</button>
      <button type="reset" class="btn-clear" onclick="window.location.href='/'">クリア</button>
    </div>
  </form>
  {result_html}
</div>
</body>
</html>"""


def parse_post_body(environ):
    """
    WSGI環境からPOSTボディを読み取り、key=value形式の辞書に変換する。

    引数:
        environ (dict): WSGIのenviron辞書。例: {{"REQUEST_METHOD": "POST", ...}}

    戻り値:
        dict: フォームの値の辞書。例: {{"height": "170", "weight": "65"}}
    """
    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
    except ValueError:
        content_length = 0

    body = environ["wsgi.input"].read(content_length).decode("utf-8") if content_length > 0 else ""

    result = {}
    for pair in body.split("&"):
        if "=" in pair:
            key, _, value = pair.partition("=")
            # 簡易unquote（標準ライブラリのurllib.parseを使用）
            from urllib.parse import unquote_plus
            result[unquote_plus(key)] = unquote_plus(value)
    return result


def app(environ, start_response):
    """
    WSGIアプリケーション本体。

    引数:
        environ (dict): WSGIサーバーから渡されるリクエスト情報。
        start_response (callable): レスポンスのステータス・ヘッダーを送信する関数。

    戻り値:
        list[bytes]: レスポンスボディ（UTF-8エンコード済み）
    """
    method = environ.get("REQUEST_METHOD", "GET")

    height_val = ""
    weight_val = ""
    result_html = ""

    if method == "POST":
        form = parse_post_body(environ)
        height_val = form.get("height", "")
        weight_val = form.get("weight", "")

        bmi, judge = calc_bmi(height_val, weight_val)
        if judge == "計算不可":
            result_html = """
  <div class="result">
    <div class="judge">身長・体重を正しく入力してください。</div>
  </div>"""
        else:
            result_html = f"""
  <div class="result">
    <div class="bmi-value">BMI: {bmi}</div>
    <div class="judge">判定: {judge}</div>
  </div>"""

    html = render_page(height_val, weight_val, result_html)
    body = html.encode("utf-8")

    status = "200 OK"
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


def main():
    """
    サーバーを起動する。
    PORT環境変数があればそれを使用し、なければ8000番を使う（ローカル/Render共通）。
    """
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    with make_server(host, port, app) as httpd:
        print(f"Serving on http://{host}:{port} ...")
        httpd.serve_forever()


if __name__ == "__main__":
    main()