#!/usr/bin/env python3
"""Simple Flask API exposing a stub equation solver."""

from __future__ import annotations

import os
from flask import Flask, jsonify, request, url_for, current_app
from sympsolve.equation_solver import equation_solver
import uuid



def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):  # type: ignore[override]
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.get("/solve")
    def solve():
        equation = (request.args.get("equation") or "").strip()
        if not equation:
            return jsonify({"error": "Missing 'equation' query parameter"}), 400
        

        filename = f"plot_{uuid.uuid4().hex}.png"
        static_plots = os.path.join(current_app.root_path, "static", "plots")
        os.makedirs(static_plots, exist_ok=True)
        plot_path = os.path.join(static_plots, filename)

        solution = equation_solver(equation, plot_filename=plot_path)


        solution["figure_url"] = url_for("static", filename=f"plots/{filename}", _external=False)
        try:
            return jsonify({"result": solution['solution'], "figure_url": solution["figure_url"]})
        except KeyError:
            return jsonify({"error": solution.get('error', 'Unknown error')}), 400

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({"message": "Equation API. Try /solve?equation=1+1"})

    return app


def run() -> None:
    port = int(os.environ.get("PORT", 8000))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    run()
