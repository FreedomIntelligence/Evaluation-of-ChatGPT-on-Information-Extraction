from chatgpt_wrapper import ChatGPT

bot = ChatGPT()
bot.refresh_session()

response = bot.ask("please output the following sentence: This is the origin session.")
print(response)  # prints the response from chatGPT

bot.new_conversation()
response = bot.ask("please output the following sentence: This is the second session.")
print(response)  # prints the response from chatGPT
