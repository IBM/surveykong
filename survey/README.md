# Overview of how this works

## There are three main pieces:
1. Taxonomy/organization of campaigns and projects
2. Surveys, questions and parts
3. Survey logic AKA: Campaigns


# 1. Taxonomy: domains, projects, campaigns, responses

From the top down: 
- Domains contain projects
- Projects have survey campaigns
- Campaigns have responses

From the bottom up: When a response to a survey comes in (a web form submission) we know what campaign it is for. A campaign belongs to a project (ex: VotE intercept campaign for w3 Home page), and to group projects, a project belongs to a domain. A domain serves little-to-no-purpose in BeeHeard.

As a visual:

<img src="../docs/taxonomy_hierarchy.png?raw=true" alt="Taxonomy diagram" width="200">


# 2. Surveys: Surveys, pages, questions, ordering

If this were a simple setup with not many, or all unique surveys, you'd make a survey and add questions to it in the order you want. However, our surveys allow you to have pages, which are ordered. And on pages there are questions, which are ordered. And surveys can be reused across projects, as well, used as a template and customized per campaign. This is designed for maximum flexibility, scalability, reusability, and all the abilities.

A survey is technically literally nothing more than a web form with fields. I would have called it forms, but these forms are specifically asking questions and getting feedback from users, so they are called "surveys". A survey has pages which have questions. It's that simple.

As a visual:

<img src="../docs/survey_hierarchy.png?raw=true" alt="Survey diagram" width="600">

### Why don't questions have an order # and go directly on a survey?

If the sort order was tied directly to the question model then you could never use that question on another survey in a different order, or even different page. You'd have to replicate that question to put it in a different order on another survey. Therefore the question order is decoupled from the question and is tied to a page, which is tied to a survey. This data architecture allows for scalable infinite reuse and customizing.


# 3. Survey logic AKA: Campaigns

### What is a campaign, what's the difference from a survey, and why do we have campaigns?

Simply put: A campaign is the way in which a project wants to use a particular survey: Project + Survey + settings = Campaign.

Explained: Suppose you have an intercept survey (it automatically pops up on the page). Project A wants to show it to 100% of the visitors. Project B wants to use the same survey, but they want to show it to 50% of the visitors and only for repeat visitors. If the settings were tied to a survey, you would have to replicate the entire survey simply to use it differently for Project B. Hence a "campaign". It's the way in which a project uses a survey. 

Think of it like an advertising campaign... A company is promoting a product, they have a TV campaign which will have a different budget and be created differently than their magazine campaign for the same product. One product, two different campaigns based on how you want to promote the product to the user. Same concept here... you have a survey (product), two different campaigns for the ways in which you are presenting that survey (product) to users.

### Campaign

Now that we've established a campaign is how a particular project wants to use a survey, let's look at how that works:

A campaign is the brains of the operation. It has the project-specific settings like "enable/disable on date ____", stop when we get ### responses, etc. It also controls how and when the survey is displayed to the user. Without a campaign, nothing exists to the visitors.

A project can have multiple campaigns: One might be a "standalone" survey that can only be accessed by a URL that you would send out in an email. One might be an intercept that gets shown to 50% of the web site visitors, and one might be a button on the side of the browser viewport where visitors can submit feedback. As well, campaigns can be enabled/disabled, time-bombed with start/stop dates, and even "inactive" (enabled, but not past a start date, or maybe past a response limit). There is a specific series of logic that happens in determining if a survey should be shown to a visitor.

A project is the heart of it all. An app or a web site or just a "thing" is a project. It's what campaigns are based on, and it's how they are shown... campaigns are "per project". So if you have a web site and you want to use a survey on your site, you setup a project for it, you get a project ID, and you embed the project-specific JS on your pages. If you have a survey you want to send out via email, like maybe a new feature wish list or priority mapping... you create a project for that.

### How embedded surveys work

Each site that wants a survey on their pages embeds the project-specific JS (`preconfig.js`) on their page using their specific project ID. This is the `preconfig_javascript` view.

`preconfig_javascript` view outputs basic JS with the project ID and runs on the page to get information about the page (currently just the URL), and requests the project config (`config.js`) with it. This second JS is the main gig that does everything on the page. It's the `project_config_javascript` view.

`project_config_javascript` view (AKA `config.js`) is the main gig. It receives the current page URL from `preconfig.js`, and it knows the ID (in the requested URL) and now runs logic to determine what JS to return to the page for execution; should it show a survey, a button, a reminder, or do nothing.

The project config function runs through a series of logic to determine:
1. Is there an intercept survey to show or show a reminder for.
2. Is there a button to show.

**There can only be one intercept and one button match to show on a page.**


### Campaign logic

Determining if there is an intercept or button-triggered campaign to show is fairly simple.
It is a two-step process:

#### 1. Find a single active intercept and single active button campaign

- Is there an **active** campaign **without** a set URL match string for this project.
- Is there an **active** campaign **with** a URL match to override a non-URL matched one for this project

 
#### 2. What to do with a found campaign
If we have an active intercept or button campaign, the second step is determining what to do with them: Should we show a survey, a button, a reminder, or do nothing? This is determined by logic (explained below for an"active campaign"):

The `project_config_javascript` view renders and returns the appropriate JS to the page (`config.js`) for the browser to execute.


### `active campaign` logic

The first step in determining what to do on the page is finding an "active" campaign. 
`active` is a flag on a campaign and it is determined by a couple basic things:

1. Are we after the start date and before the stop date
2. Are we under the response count limit

"Feedback" survey and associated campaigns are normally not limited to a 1-take and are triggered by a button on the side of the browser. For 99.999% of them, there is no other logic other than looking for an active button campaign for the current page.

"Intercept/VotE" surveys are special. They are usually 1-take within 90 (or some specified #) days, and are set to show only to a certain % of visitors. Once you've been flagged to be shown the survey, you won't get shown it again within the 90 (or some specified #) days. 

If we have an active `type == intercept` campaign, the second step of logic goes *in this specific order*:
1. Have they taken it within the time period allowed (stop and do nothing)
2. Have they been flagged as already been show it (stop and do nothing)
3. Did they say "remind me later" (show the reminder icon on right side viewport)
4. Is the visitor "shown" % under the % of traffic we're supposed to show it to (show it)

If there is no campaign matched for a URL or they've already taken the campaign, there is no check for another one they haven't taken. There can only be 1 active campaign matched and checked.









