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
from fastapi_poe import PoeHandler, run

class EchoHandler(PoeHandler):
    async def get_response(self, query):
        last_message = query.query[-1].content
        yield self.text_event(last_message)

if __name__ == "__main__":
    run(EchoHandler())
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

### Cloud providers

Cloud providers such as AWS, Azure, or Heroku provide the most powerful and scalable way
to host a web service. Indeed, Poe's own servers are hosted on AWS. There are many ways
to use these services and many tutorials on how to get started, but here is a broad
guide on how to get a Poe bot running on AWS:

- Create an AWS account
- Go to EC2 and create an instance (i.e., a virtual machine). There are many different
  instance types available; to start with, you could use a small instance type like
  `t4g.nano`. If your bot's compute needs grow, you can alwaws switch to a different
  instance type later.
- SSH into your newly created instance. This requires creating a key pair, then running
  a command like `ssh -i yourkeypair.pem ec2-user@xx.xx.xx.xx` where `xx.xx.xx.xx` is
  the IP address for your instance.
- Install the code for your bot (e.g., by cloning your GitHub repo), and start the
  server.
- Create an EC2 Application Load Balancer to make your instance accessible. For now,
  make it listen only on port 80 (HTTP). Associate your instance with the load balancer.
- Go to the public URL of your load balancer, which will be something like
  name-12345678.us-east-1.elb.amazonaws.com, and confirm your bot server is accessible.
  If it is not, check that you used the right ports and that your security groups make
  the load balancer publicly accessible and allow it to access the server.
- Now you have an accessible URL, but you'll also need HTTPS. To do that:
  - Get a domain you can control
  - Use AWS Certificate Manager to issue a certificate for this domain
  - Edit your load balancer to listen on port 443 and add the certificate you just
    created
- Confirm your bot URL is now accessible using HTTPS

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
