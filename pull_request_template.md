# Pull Request - Added Functionality to Kai Loaders

## Summary
Created new loaders to handle docx, pptx, csv, txt, youtube links, and web links
Created Unit tests to test these new loaders and to test multiple loaders at once

## Changes
Renamed BytesFilePDFLoader to PDFLoader for consitency with the other loaders
Made a class for each loader
- PDFLoader
- DOCXLoader
- PPTXLoader
- CSVLoader
- TXTLoader
- YouTubeLoader
- WebPageLoader
Routed to these loaders using URLLoader for seamless integration

## Testing
The loaders were tested with manual testing and unit tests using pytest
- Manual testing covered mutltiple questions and multiple files for each loader
- Used offensive testing practices to identify any issues with the loaders and how to use the API
- Unit tests were made for each loader, and tests that the loader can generate a Document from a URL
- Another unit test was created to test if it could generate a Document from multiple files

## Results
Created a series of new loaders that add functionality to Kai
Screenshots of this working are here: https://docs.google.com/document/d/15Vqf3E2PuZtapccfHPSYOCcIGJbXaYGUr3e3AZ9DfHs/edit?usp=sharing

## How to Test
Open up the API using whatever method works best for you and use these sample JSON requests to test each loader