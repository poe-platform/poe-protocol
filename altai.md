# Altaibot

Most users of the Poe protocol will be Large Language Models (LLMs)
that perform some useful task for users. But for this example, we'll
instead build a Small Cat Model (SCM) representing Altai. Altai is
Jelle's cat. He is a simple cat with just a few behaviors:

* He likes to eat cardboard. If he receives a message that contains
  the string "cardboard", he responds with "crunch crunch".
* He likes to beg for food. If he receives a message that contains
  one of the strings "kitchen", "meal", or "food", he responds with
  "meow meow". He suggests the reply "Feed Altai".
* Otherwise, he sleeps. He responds with "zzz".

In the examples in this repo, we will implement the Altaibot SCM.
