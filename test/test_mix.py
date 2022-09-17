import filecmp
import json
import os
import unittest

import pytest

import gradio as gr
from gradio import mix
from gradio.external import TooManyRequestsError

"""
WARNING: Some of these tests have an external dependency: namely that Hugging Face's Hub and Space APIs do not change, and they keep their most famous models up.
So if, e.g. Spaces is down, then these test will not pass.
"""

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"


class TestSeries:
    def test_in_interface(self):
        io1 = gr.Interface(lambda x: x + " World", "textbox", gr.Textbox())
        io2 = gr.Interface(lambda x: x + "!", "textbox", gr.Textbox())
        series = mix.Series(io1, io2)
        assert series("Hello") == "Hello World!"

    def test_in_interface_img(self):
        io1 = gr.Interface(lambda x: x, "image", gr.Image())
        io2 = gr.Interface(
            lambda x: "gradio/test_data/cheetah2.jpg", "image", gr.Image()
        )
        series = mix.Series(io1, io2)
        out = series("gradio/test_data/cheetah1.jpg")

        assert filecmp.cmp(out, "gradio/test_data/cheetah2.jpg")

    @pytest.mark.flaky
    def test_with_external(self):
        io1 = gr.Interface.load("spaces/abidlabs/image-identity")
        io2 = gr.Interface.load("spaces/abidlabs/image-classifier")
        series = mix.Series(io1, io2)
        try:
            output = series("gradio/test_data/lion.jpg")
            assert json.load(open(output))["label"] == "lion"
        except TooManyRequestsError:
            pass


class TestParallel:
    def test_in_interface(self):
        io1 = gr.Interface(lambda x: x + " World 1!", "textbox", gr.Textbox())
        io2 = gr.Interface(lambda x: x + " World 2!", "textbox", gr.Textbox())
        parallel = mix.Parallel(io1, io2)
        assert parallel("Hello") == ["Hello World 1!", "Hello World 2!"]

    def test_multiple_return_in_interface(self):
        io1 = gr.Interface(
            lambda x: (x, x + x), "textbox", [gr.Textbox(), gr.Textbox()]
        )
        io2 = gr.Interface(lambda x: x + " World 2!", "textbox", gr.Textbox())
        parallel = mix.Parallel(io1, io2)
        assert parallel("Hello") == [
            "Hello",
            "HelloHello",
            "Hello World 2!",
        ]

    @pytest.mark.flaky
    def test_with_external(self):
        io1 = gr.Interface.load("spaces/abidlabs/english_to_spanish")
        io2 = gr.Interface.load("spaces/abidlabs/english2german")
        parallel = mix.Parallel(io1, io2)
        try:
            hello_es, hello_de = parallel("Hello")
            assert "hola" in hello_es.lower()
            assert "hallo" in hello_de.lower()
        except TooManyRequestsError:
            pass


if __name__ == "__main__":
    unittest.main()
