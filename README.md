# Smart Study

AI Analytics tool that can analyze your study pattern and give personalized recommendations. Video demo: https://www.youtube.com/watch?v=QiAafRyXsr0&ab_channel=BowenFeng. A walkthrough of how to use the product is contained in the promo video.

## Running from source

We have a deployed version here: https://smart-study-webapp.herokuapp.com/, and all components including extension, desktop can be downloaded from our deployed website. However, if you do want to run from source, please do the following:

1. Install .NET Framework 4.7.2 and Visual Studio 2019 or above
2. Install Python, and all required libraries in each of the 5 components
3. Install npm node and all required node modules

Run the 2 Python Flask servers in the backend folder, and run the React server by using the command "npm start". You can find the Visual Studio solution file in the desktop folder. The chrome extension can be loaded directly into chrome.

However, we do not recommend locally running from source, and instead encourage you to utilize our deployed app, as running from source requires replacing several request endpoints, as those has been set to the production servers (as opposed to the local development servers). The code is purely for educational and informational purposes.
