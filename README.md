## What it does

BudgetBuddy is a straightforward tool that helps users confidently start investing in real estate based on their unique financial situation. After answering a few questions about income, debt, savings, and location, users receive a personalized price range and see live property listings that match their profile using a real estate API.

But we don’t just stop at listings—BudgetBuddy performs a risk analysis on each property to flag smart investments and highlight potential risks. We also offer helpful financial tools, including our popular *Round Up* savings feature and loan tracking to support users after purchase.

BudgetBuddy is built to guide users through the entire home-buying journey—from finding the right property to managing it responsibly. We’ve also integrated a chatbot powered by the generative AI model **Gemini**, providing individualized, quick responses to user queries and offering tailored guidance throughout their experience.

## How we built it

We used **Streamlit** to seamlessly integrate the front end and back end of BudgetBuddy, delivering a clean, interactive user experience. Our tech stack includes **Python**, **HTML**, **CSS**, and **JavaScript**, working together to create a responsive and intuitive interface.

To provide personalized, real-time guidance, we integrated the **Gemini API**, powering our intelligent chatbot assistant. For property discovery, the **Realtor API** allows us to search thousands of real estate listings and surface the best investment opportunities through our *Property Search* feature.

On the financial side, we used **Capital One’s Nessie API** to simulate customer accounts and transactions. This enabled us to build our custom *Round Up* feature, which automatically sets aside spare change from user purchases into savings—mirroring real-world behavior.

Together, these technologies brought BudgetBuddy to life as a smart, supportive guide for aspiring homeowners.

## Challenges we ran into

One of our biggest challenges was integrating multiple APIs with different data formats and authentication methods. Coordinating between the **Realtor API** for property listings, **Gemini** for our chatbot, and **Capital One’s Nessie API** for simulated transactions required careful data handling and timing.

Another challenge was designing a user experience that could take complex financial information and present it in a way that’s simple, helpful, and friendly. We wanted users to feel empowered—not overwhelmed—so it took time to strike the right balance between depth and usability.

Finally, connecting all parts of the system through **Streamlit** while maintaining performance and a smooth UI pushed us to think creatively about structure, optimization, and flow.

Despite these obstacles, we’re proud of how cohesive and functional BudgetBuddy became—and we learned a ton along the way.

## Accomplishments that we're proud of

We’re proud of how much ground we were able to cover with BudgetBuddy—both in functionality and user experience.

One major accomplishment was building a real estate search that pulls from thousands of listings and runs a risk analysis to help users quickly identify smart investment opportunities.

We also developed an entire simulated customer database using **Capital One’s Nessie API**, allowing us to bring our *Round Up* savings feature to life with realistic transactions.

Another highlight was integrating live calls to the **Gemini API** to power our chatbot, giving users fast, informative answers to their real estate and finance questions in a natural, conversational way.

Most of all, we’re proud that we brought all these powerful tools together in a website that remains simple, approachable, and genuinely helpful.

## What we learned

Through the development of BudgetBuddy, we learned how to efficiently build interactive web applications using **Streamlit**, significantly reducing development time and allowing us to focus on refining other features. We also gained the ability to integrate API calls seamlessly, handling large datasets with ease to ensure smooth functionality. By incorporating **Gemini AI**, we enhanced the platform's capabilities, automating processes and improving the user experience. Additionally, we learned to design and implement intuitive, user-friendly interfaces, ensuring the website is accessible and engaging for all users.

## What's next for BudgetBuddy

Next for BudgetBuddy, we plan to enhance the AI-powered property matching system, providing personalized recommendations based on user preferences and budgets to streamline the property search. We’re also looking to connect users with real estate agents for virtual tours, enabling live walkthroughs and real-time interactions to make the property-buying process more efficient and interactive.

To scale the project further, we will focus on optimizing performance and integrating more APIs, expanding our database of properties, and enhancing machine learning models to provide even more accurate, relevant investment recommendations to a growing user base.
