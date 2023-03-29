# Altaibot

Most users of the Poe protocol will be Large Language Models (LLMs) that perform some
useful task for users. But for this example, we'll instead build a Small Cat Model
(SCM). This example is intended to cover most major parts of the protocol.

The SCM represents Altai. Altai is Jelle's cat. He is a simple cat with just a few
behaviors:

- He likes to eat cardboard. If he receives a message that contains the string
  "cardboard", he responds with "crunch crunch".
- He likes to beg for food. If he receives a message that contains one of the strings
  "kitchen", "meal", or "food", he responds with "meow meow". He suggests the reply
  "Feed Altai".
- Altai doesn't like strangers, and if he sees one he hides and periodically checks if
  it's safe to come out. If a message contains "stranger", he responds "peek" 10 times,
  with a one-second wait in between.
- Altai doesn't like to eat square cat snacks and gets confused when he sees one. If a
  message contains "square", he responds with an error message. If a message contains
  "cube", he gets even more confused and produces an error that does not allow retries.
- Altai is proficient in text rendering technologies. He responds in Markdown by
  default, but if the message contains "plain" he responds in plain text. If the message
  contains "markdown", he gets excited and sends a message demonstrating his knowledge
  of markdown.
- Otherwise, he sleeps. He responds with "zzz".

In the examples in this repo, we will implement the Altaibot SCM.
