from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import requests
from flask import Flask, send_file, jsonify, render_template, request
from flask_cors import CORS

MAX_CURRENTS_AMOUNT = 100

app = Flask(__name__, template_folder='template')
CORS(app)


def magnetic_field_wire(I, x, y, x0, y0):
    mu0 = 4 * np.pi * 1e-7
    r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
    theta = np.arctan2(y - y0, x - x0)
    Bx = (mu0 * I / (2 * np.pi)) * (-np.sin(theta) / r)
    By = (mu0 * I / (2 * np.pi)) * (np.cos(theta) / r)
    return Bx, By


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_plot', methods=['POST'])
def get_plot():

    plot_data = {'currents': []}

    for i in range(1, MAX_CURRENTS_AMOUNT):
        current = request.form.get(f'current{i}', type=float)
        x_position = request.form.get(f'x_position{i}', type=float)
        y_position = request.form.get(f'y_position{i}', type=float)

        if current is not None and x_position is not None and y_position is not None:
            plot_data['currents'].append([current, x_position, y_position])
        else:
            break

    currents = plot_data.get('currents', [])

    max_x = max(abs(current[1]) for current in currents)
    max_y = max(abs(current[2]) for current in currents)

    xlim = (-max_x - 2, max_x + 2)
    ylim = (-max_y - 2, max_y + 2)

    x = np.linspace(xlim[0], xlim[1], 100)
    y = np.linspace(ylim[0], ylim[1], 100)
    X, Y = np.meshgrid(x, y)

    BX_total = np.zeros_like(X)
    BY_total = np.zeros_like(Y)

    for current_data in currents:
        I, x0, y0 = current_data
        BX, BY = magnetic_field_wire(I, X, Y, x0, y0)
        BX_total += BX
        BY_total += BY

    plt.figure(figsize=(max(xlim), max(ylim)))
    plt.streamplot(X, Y, BX_total, BY_total, density=2, linewidth=1, arrowsize=2)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Magnetic field lines from direct conductors')
    plt.grid(True)
    plt.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)

    buffer.seek(0)
    plt.close()

    return send_file(buffer, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
