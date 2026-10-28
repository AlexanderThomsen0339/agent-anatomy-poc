Author: DNO
Created on: 26-10-2026
Description: This is a specification for a new AI-enhanced quality assurance tool for the sole purpose of helping out two internal teams at Aalborg Forsyning A/S. The first internal team is the engineering team, who are specialized in application development. The second internal team is the communications team, who are specialized in press, public relations, customers and end-users within the organization. The tool needs therefore to be centered around Aalborg Forsynings website and self-service, where users can see their consumptions in the household, pay their utility bills and read more information about service alerts and so on. 

The purpose itself:
The tool is a smart AI-tool that helps the users from both teams inform them about the situation of the development proces. This can be in the shape of getting insight into what was recently built on the test and production environments, what's currently being built, and so on. The system is smart enough to check the repository, and the internal documentation and other relevant data points, and hold it up against the test protocols that ultimatively validates the work in progress.

Non-functional requirements:
1) This application needs to be served as a simple web application with the Aalborg Forsyning logo
2) The application must be simple in the sense that it is user friendly and has some core visual elements: a title view, a description, a chat input.

Functional requirements:
1) All users are able to send their requests such as general prompts into the chat. 
2) The system will return a response based on investigating the code, the docs, the test protocols, in a short format.
3) Short formats for every response, and they must be non technical, and be very, very high abstract responses.

Nice to have:
It is optional at this point, but it would be very elegant if the agent can open the application and navigate itself into a specific view, and screenshot, if a recent change or contribution has resulted in a defective or malfunctioning application. (for example, Katja has changed X and Y in the code, thus resulting in View X or Y showing something wrong to the user, or a 404 page.)

Agent workflow:
1. Break down the prompt
2) Localize what the subject of the prompt is related to. Is it authentication? Is it consumption, or something completely else. 
3) Following up on step 2, it'll find the related source files under a specific module, as well as the relevant test documents, the relevant wiki pages and other system documentations (may as well be diagrams).
4) Once analyzed, the agent is free to do whatever it wants in order to achieve the ultimate goal (see specific the goal section), where the end-user of this tool will get a clear and short answer to what was made, and whether or not the test protocols can be conducted.

Ultimate goal:
Any user within the two teams can ask an AI-agent on what was recently changed, made, contributed and so on, and whether or not the new state can be passed according to its related test protocols.

Scale of business:
This is a strict POC, which means that we are not looking into infrastructure or anything other than the tool being able to run on the local machine.
