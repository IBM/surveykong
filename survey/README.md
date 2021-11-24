# Overview of how this works
There are two main pieces:
 - Survey and all it's parts
 - Taxonomy/organization of campaigns and projects
 
 # Taxonomy: domains, projects, campaigns, responses
 
 From the bottom up: When a response to a survey comes in (a form submission) we know what campaign it was for. Projects can have one or more campaigns, ex: VotE intercept campaign and a feedback button campaign. And to further organize projects, they are grouped into domains.
 
 From the top down: Domains contain projects. Projects have survey campaigns, and campaigns have responses.
 
 As a visual:
 
 <img src="../docs/taxonomy_hierarchy.png?raw=true" alt="Taxonomy diagram" width="200">
 
 # Surveys: surveys, pages, questions, ordering
 
 If this were a simple setup with not many surveys, you'd make a survey and add questions to it. However, our surveys allow you to have pages, and on pages there are questions. This is designed for maximum flexibility, scalability, reusability, and all the abilities. :)
 
 ## Why don't questions have an order # and go directly on a survey?
 
 If the sort order was directly on a question model, then you could never use that question on another survey, but in a different order. You'd have to replicate that question simple to put it in a different order on another survey. Thus the question order is decoupled from the question and is tied to a page, which is tied to a survey.
 
 ## What is a campaign, what's the difference from a survey, and why do we have those?
 
 A survey is nothing more than literally a web form. I would have called it forms, but these forms are specifically asking questions and getting feedback from users, so they are called surveys.
 
 From the bottom up: A campaign is the settings for how a project wants to use a survey. Campaign = Project + Survey + settings. Questions belongs to a page, in a specific order. Pages belong to a survey, in a specific order. And a survey is used by a project in a campaign, with certain settings.
 
 A campaign is the settings and way in which a project uses a survey. Suppose you have an intercept form. Project A wants to show it to 100% of the users. Great. Project B wants to use the same survey, but they want to show it to 50% of the users and only repeat visitors. If the settings were tied to a survey, you would have to replicate the entire survey simply to use it different for Project B. Hence a "campaign". It's the way in which a project uses a survey. Think of it like an advertising campaign. A company is promoting a product, they have a TV campaign what will be a different budget and created differently than their magazine campaign for the same product. One product, two different campaigns based on how you want to promote the product to the user. Same conecpt here... you have a survey, two different campaigns in which you are presenting that survey to users.
 
As a visual:

<img src="../docs/survey_hierarchy.png?raw=true" alt="Survey diagram" width="600">


