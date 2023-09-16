//This is an iframe embed code, not a link. The embed code is video dependent. I know we typically like to avoid stringified HTML, but this is a notable exception where the HTML is designed for this exact use-case.
// const heroLink = '<iframe width="100%" height="600px" src="https://www.youtube.com/embed/5atxB5RRUvI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';

const RIGHT_CLICK_SAVE_SELECTION =
  'https://storage.googleapis.com/pieces_multimedia/PROMOTIONAL/PIECES_FOR_DEVELOPERS/JUPYTER/MACOS/RIGHT_CLICK_SAVE_SELECTION/16X9/PIECES_FOR_DEVELOPERS-JUPYTER-RIGHT_CLICK_SAVE_SELECTION-16X9-MACOS-6_22_2023.gif';
const EMBEDDED_BUTTON_SAVE_ACTIVE_CELL =
  'https://storage.googleapis.com/pieces_multimedia/PROMOTIONAL/PIECES_FOR_DEVELOPERS/JUPYTER/MACOS/EMBEDDED_BUTTON_SAVE_ACTIVE_CELL/16X9/PIECES_FOR_DEVELOPERS-JUPYTER-EMBEDDED_BUTTON_SAVE_ACTIVE_CELL-16X9-MACOS-6_22_2023.gif';
const SEARCH_AND_INSERT =
  'https://storage.googleapis.com/pieces_multimedia/PROMOTIONAL/PIECES_FOR_DEVELOPERS/JUPYTER/MACOS/SEARCH_AND_INSERT/16X9/PIECES_FOR_DEVELOPERS-JUPYTER-SEARCH_AND_INSERT-16X9-MACOS-6_22_2023.gif';
const SNIPPET_BUTTON_SHARE =
  'https://storage.googleapis.com/pieces_multimedia/PROMOTIONAL/PIECES_FOR_DEVELOPERS/JUPYTER/MACOS/SNIPPET_BUTTON_SHARE/16X9/PIECES_FOR_DEVELOPERS-JUPYTER-SNIPPET_BUTTON_SHARE-16X9-MACOS-6_22_2023.gif';
const WITH_DESKTOP_APP =
  'https://storage.googleapis.com/pieces_multimedia/PROMOTIONAL/PIECES_FOR_DEVELOPERS/JUPYTER/MACOS/WITH_DESKTOP_APP/16X9/PIECES_FOR_DEVELOPERS-JUPYTER-WITH_DESKTOP_APP-MACOS-6_22_2023.png';

export const onboardingMD = `

# Elevate Your Jupyter Experience with Pieces

<div class="nav">
    <a href="https://docs.pieces.app/extensions-plugins/jupyterlab" style="display: inline-block; text-decoration: none; border-radius: 4px;">Docs</a>		<a href="https://pieces.app" style="display: inline-block; text-decoration: none; border-radius: 4px;">Learn More</a>
</div>

## Your Guide to Getting Started with Pieces for Developers Jupyter Extension

#### 1. Save your first snippet
- To save a snippet, highlight the text, right-click, and select "Save to Pieces."
![Save to Pieces via Menu](${RIGHT_CLICK_SAVE_SELECTION})

**Additional ways to save**
- Click the Pieces Save button within any code block.
![Save to Pieces via Button](${EMBEDDED_BUTTON_SAVE_ACTIVE_CELL})


#### 2. Find & use your snippets
- To access your saved snippets, click on the Pieces icon in your left sidebar.
![Search Your Pieces](${SEARCH_AND_INSERT})


#### 3. Share your Snippets
- Collaborate with others with ease using shareable links for your snippets
![Share you Snippets](${SNIPPET_BUTTON_SHARE})


### Maximize productivity with our Flagship Desktop App
Utilize the Pieces [Flagship Desktop App](https://pieces.app) in combination with our Jupyter Plugin to streamline your workflow and enhance your development productivity.

- Get back in flow with our Workflow Activity View
- Save time with In-Project Snippet Discovery
- Enjoy real-time and scope-relevant suggestions
- Extract and use code and text from screenshots
![Save to Pieces via Button](${WITH_DESKTOP_APP})

<div class="nav">
    <h3>Socials</h3>
</div>
<div class="nav">
    <a href="https://discord.gg/5AN7rVXEES" style="display: inline-block; text-decoration: none; border-radius: 4px;">Discord</a>		<a href="https://www.youtube.com/@getpieces" style="display: inline-block; text-decoration: none; border-radius: 4px;">YouTube</a>		<a href="https://twitter.com/@getpieces" style="display: inline-block; text-decoration: none; border-radius: 4px;">Twitter</a>		<a href="https://www.linkedin.com/company/getpieces" style="display: inline-block; text-decoration: none; border-radius: 4px;">LinkedIn</a>		<a href="https://www.facebook.com/getpieces" style="display: inline-block; text-decoration: none; border-radius: 4px;">Facebook</a>
</div>
`;
