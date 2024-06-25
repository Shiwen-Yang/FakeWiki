## How do I run this???
Simple, first install Ollama [here](https://ollama.com/download), then pull your model of choice. The one I used is [Llama 3 8B Instruct](https://ollama.com/library/llama3) which works really well and is very impressive for an 8B model. If you don't want to use Ollama you can use any other OpenAI-compatible server by modifying the `client` declaration in Engine.py to link to your server, I recommend [llama.cpp's server example](https://github.com/ggerganov/llama.cpp/tree/master/examples/server) for something lightweight, or [text-generation-webui](https://github.com/oobabooga/text-generation-webui/) for a fully featured LLM web interface.

Due to popular demand and it not being 12am anymore I finally added a requirements.txt file! Now instead of manually installing dependencies you can just run `pip install -r requirements.txt` in the root of the project and it'll install them all for you!

(If you want to manually install dependenies, follow these instructions) Next you'll need to install Python if you don't already have it, I run Python 3.10.12 (came with my Linux Mint install), then the libraries you'll need are:
- [OpenAI](https://pypi.org/project/openai/)
- [Flask](https://pypi.org/project/Flask/)
- [jinja2](https://pypi.org/project/Jinja2/)

Once those are installed, simply run the main.py file and navigate to http://127.0.0.1:5000 or whatever URL Flask gives you and have fun!

## Inspiration
I'll admit it, I'm not the most creative person. I got this idea from [this reddit comment on r/localllama](https://new.reddit.com/r/LocalLLaMA/comments/1c6ejb8/comment/l02eeqx/), so thank you very much commenter!
