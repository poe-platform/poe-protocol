# Catbot

Most users of the Poe protocol will be Large Language Models (LLMs) that perform some
useful task for users. But for this example, we'll instead build a Small Cat Model
(SCM). This example is intended to cover most major parts of the protocol.

The SCM represents Altai. Altai is Jelle's cat. He is a simple cat with just a few
behaviors:

- He likes to eat cardboard. If he receives a message that contains the string
  "cardboard", he responds with "crunch crunch".
- He likes to beg for food. If he receives a message that contains one of the strings
  "kitchen", "meal", or "food", he responds with "meow meow". He suggests the reply
  "Feed the cat".
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
- Altai can count. If you send a message that contains "count", he replies with "1",
  waits a second, then replaces his response with "2", and so on until 10. If you add
  "quickly", he doesn't sleep while counting.
- If you give Altai scratches (by sending a message containing "scratch"), he gets so
  excited that he forgets how the Poe protocol works, and sends back an event with type
  "purr". (Since this is not allowed by the protocol, it will trigger a call to the
  `report_error` endpoint from the Poe server.)
- If you call Altai a dog, he doesn't want to talk to you any more. If the message
  contains "dog", he turns off suggested replies.
- If you give him a toy, he keeps hitting it, more than is allowed by the Poe protocol
  spec. If a message contains "toy", he sends more than 1000 events that contain the
  text "hit ".
- If Altai gets on a bed, he doesn't stop sleeping. If a message contains "bed", he
  sends a "zzz" response with over 10000 letters, more than the Poe protocol allows.
- Otherwise, he sleeps. He responds with "zzz".

In the examples in this repo, we will implement the Catbot SCM.
