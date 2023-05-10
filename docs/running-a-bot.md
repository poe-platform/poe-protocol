# Running a bot

Any Internet-accessible service can work as a Poe bot. As long as you follow
[the protocol](./spec.md), you can set up the service in any way that you are
comfortable with, using whatever programming language, server technology, and hosting
provider you prefer. However, to make the job easier, this document provides some
guidance on how to implement a bot.

If you have any questions, join us on [Discord](https://discord.gg/TKxT6kBpgm).

## Writing your bot

If you are writing your bot in Python, you can use our
[fastapi-poe](https://pypi.org/project/fastapi-poe/) project as a base. You can install
it with e.g. `pip install fastapi-poe`, or using your favorite way of managing Python
packages.

Here is a simple bot that uses `fastapi-poe` just to echo the user's message:

```python
from fastapi_poe import PoeBot, run

class EchoBot(PoeBot):
    async def get_response(self, query):
        last_message = query.query[-1].content
        yield self.text_event(last_message)

if __name__ == "__main__":
    run(EchoBot())
```

To get it running, save it in a file called `echobot.py` and run `python echobot.py`.

Of course, real bots should do something more interesting than echoing back the user's
message. We provide more advanced examples that interact with
[LangChain](https://python.langchain.com/en/latest/index.html) and
[LlamaIndex](https://github.com/jerryjliu/llama_index), which allows you to build your
bot on top of existing LLMs and add additional powerful features:

- [langchain-template-poe-fastapi](https://github.com/langchain-ai/langchain-template-poe-fastapi)
  provides examples that have a conversation memory or that allow users to ask questions
  about a document.
- [llama-poe](../llama_poe/README.md) provides knowledge-enhanced bots that have
  knowledge about specific documents.

## Hosting your bot

Now that you have written your bot, you need to make it Internet-accessible so that the
Poe servers can talk to it.

We'll cover three ways to do it:

- Using `ngrok` to make a bot running on your local computer Internet-accessible. This
  is easy to set up, but works only as long as your computer is connected to the
  Internet.
- Using `Replit` to host your bot on an online IDE. This is also easy to set up, but the
  resources available to the bot server will be limited.
- Using a cloud provider such as AWS. This is the most powerful and scalable approach,
  but also the most work to set up.

### ngrok

[ngrok](https://ngrok.com/) is a tool to add Internet connectivity to any service. You
can use it, for example, to make a Poe bot running on your local computer accessible on
the Internet:

- Install ngrok ([instructions](https://ngrok.com/download))
- Start your bot server, e.g. with `python yourbot.py`
- Confirm that it is running locally by running `curl localhost:8080`
- Run `ngrok http 8080` in another terminal and note the URL it provides, which will
  look like `https://1865-99-123-141-32.ngrok-free.app`
- Access that URL in your browser to confirm it works

### Replit

[Replit](https://replit.com/) is a browser-based IDE. Among other features, it allows
you to run a publicly accessible Web service in your project. To get started:

- Go to the [Poe API template](https://replit.com/@JelleZijlstra2/Poe-API-Template?v=1)
- Click "Use this template"
- Modify the template to behave the way you want
- Click "Run"
- Note the URL in the address bar above "FastAPI Poe bot server" (see screenshot)

![Screenshot of a Replit page with the URL for the server circled.](./images/replit.png)

### Heroku

[Heroku](https://heroku.com) is a platform that makes it easy to deploy simple apps. We
provide a sample repository to deploy a Poe bot to Heroku:
[https://github.com/poe-platform/heroku-sample](heroku-sample). Check out that
repository for detailed instructions.

### Cloud providers

Cloud providers such as AWS, Azure, or Google Cloud provide the most powerful and
scalable way to host a web service. Indeed, Poe's own servers are hosted on AWS.
However, such services also require the most setup and configuration, so we only
recommend switching to such a service if you really outgrow what is possible on simpler
platforms. There are many ways to use these services and many tutorials on how to get
started. In general, you'll need to perform something like the following steps:

- Create a server virtual machine (often called instance)
- Install your bot and its dependencies on the server
- Run your Poe bot on that server (e.g., `python -m fastapi_poe`)
- Register a domain name (e.g. "mypoebot.com")
- Create a TLS certificate for the domain
- Create a networking interface (e.g., a load balancer) that is connected to your
  domain, your TLS certificate, and your server

## Connecting your bot to Poe

Once you have a bot running under a publicly accessible URL, it is time to connect it to
Poe. You can do that on poe.com at
[the bot creation form](https://poe.com/create_bot?api=1). You can also specify a name
and description for your bot. After you fill out the form, your bot should be ready for
use in all Poe clients!

### API keys

To connect your bot to Poe, you'll have to set an API key (see
["Authentication" in the spec](./spec.md#authentication)). There are three ways:

- `fastapi_poe` will generate an API key and print it to the server if you don't provide
  one explicitly. Run the server, note the API key it prints out, and use that key to
  the bot creation form.
- Pass the key as an argument to the `fastapi_poe.run` function. This is the easiest
  approach in Replit.
- Pass the key as an environment variable `POE_API_KEY`.
