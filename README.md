HOW TO RUN

1. Install ollama

2. Download all jsons from data and put them in folder named 'data' without changing any names

3. Run main.py

Code may take 1-4 min for generating response (depending on device). Please wait for response.


**College Advisor**
--------------------

Trials:

1.	RAG: Tried implementing RAG since it seemed the most suitable. However no success since :

    a. Data was mostly numerical (RAG needs large amounts of textual data for LLM to train on)
  	
    b. The only sources of data are govt sites (NTA) but are limited in info.
  	
    c. There are no APIs so no live retrieval has been implemented.
  	
    d. Rank vs Marks jsons when vector embedded kept being treated as word tokens and giving incorrect results.

3.	Regex: Requires prompts in a very specific way which is not what the task demands.

Hence, I stuck to a hybrid which uses LLMs for dealing with natural language and some logic for querying the data.




Working (overview):
1.	User enters natural prompt
2.	LLM extracts parameters (rank, gender, exam, marks, branch)
3.	Prompt is classified as ‘general’ or ‘structured’
4.	If structured => parameters are extracted => seats are filtered 
5.	Answers are compiled and sent back to LLM which responds to user
6.  Memory updated for future use




Pros:
1.	Database is 100% accurate and reliable for cutoffs
2.	LLM can respond to general queries such as ‘best books for jee’ as well

Cons:
1.	Typos: Misspelling/abbreviations/nicknames of branches or college names can throw the agent off (Eg: Trichy != Tiruchirappalli)
2.	Prompt: For the database query to trigger, prompt must have marks + either college OR branch 
3.	Memory: Since a new instance of the agent is being called every time agent does not recall previous information. 

However, a makeshift memory has been implemented which helps the agent recall with decent results but not reliable for complex memory tasks.



What can be better?
For a hybrid model as such, the only improvements can be in better prompts, improving logic (such as setting a filter for displaying the best 5 colleges from available options) and diversifying exams.
Best performance would be by implementing RAG. The only issue being: getting accurate data for the hundreds of colleges + placement data + campus information instead of simple JSONs by scraping (not possible with NTA, and would rather not use Shiksha.com or unreliable websites).





**Sample Run (if running code not possible):**
--------------------------------------------------

(Some observations mentioned in brackets by me, not the agent)

('...' used by me to indicate that LLM continues with rest of the answer)

Starting...
Agent: Namaste!I'm thrilled to help you explore the best engineering colleges in India. It's exciting that you're considering pursuing your passion for engineering, and I'm here to guide you through the process. What sparked your interest in engineering, and what are your expectations from an ideal college experience?


--------------------------------------------------
Type 'exit' or 'quit' to end the conversation.

You: what can i get in iit bombay with 180 marks?
(iit Bombay, 180, jee adv, gender-neutral extracted) 

Agent: Hey there!
I've got some exciting options for you based on your JEE Advanced rank and preferences. Since you're eligible for several programs at IIT Bombay, let's dive into each of them:
**Chemistry (4 Years, Bachelor of Science) at Indian Institute Of Technology Bombay**
This program is designed to provide a solid foundation in chemistry and its applications. You'll explore topics like analytical techniques, physical chemistry, and After graduation, you can pursue careers in....
**Your rank: 4101**
**Environmental Science and Engineering (4 Years, Bachelor of Technology) at Indian Institute Of Technology Bombay**
This program....				     
(continues to list programs I am eligible for in IITB)
________________________________________________________

You: how is the campus life over there?				             
(IITB NOT mentioned to test memory)

Agent: Campus life at IIT Bombay is truly vibrant and exciting! As one of the oldest and most prestigious engineering institutions in India, IIT Bombay offers a....			       
(IITB used from memory)
________________________________________________________

You: should i take a drop instead? 						
(again, no information given)

Agent: The age-old dilemma of whether to take a drop or not!
As your advisor, I'd like to weigh in on this decision. Since you've already secured admission to IIT Bombay with 180 marks, it's essential to consider the pros and cons of taking a drop.... 		        
(agent memory working)
________________________________________________________

You: end

Goodbye!
________________________________________________________
