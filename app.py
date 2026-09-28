from flask import Flask, render_template, request
import matplotlib.pyplot as plt

app = Flask(__name__)

# nhanh master - test conflict
@app.route("/", methods=["GET", "POST"])
def index():
    male = None
    female = None

    if request.method == "POST":
        male = int(request.form["male"])
        female = int(request.form["female"])

        // du lieu de ve bieu do
        labels = ["Nam", "Nữ"] // ten cot
        values = [male, female] // so luong sv

        plt.figure() // tao hinh ve moi
        plt.bar(labels, values) // tao bieu do cot
        plt.xlabel("Giới tính")
        plt.ylabel("Số sinh viên")
        plt.title("Số lượng sinh viên nam và nữ")

        plt.yticks(range(0, max(values) + 2))

        plt.savefig("static/chart.png")
        plt.close()

    return render_template(
        "index.html",
        male=male,
        female=female
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5175)