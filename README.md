# Jack J Williams Portfolio

Contains publicly available projects that I have been working on. No project/data contains sensitive information.

Note that some of these projects were created at the start of my Python career and will not reflect my current coding standards!

A private directory is available that contains the productionised code used to create the dataset for the League of Legends Analytics site Jung.GG, but permission is granted only to those with agreeable circumstances (recruiters/colleagues/friends) given my desire to keep our methods safe from competitors!

## Current Portfolio:

**CNN - Music Genre Classification**: Building a CNN model capable of classifying the genre of a song based on a 30 sec extract. First transforms the audio files into melospectrograms (images of sound over time). Builds a base LeNet model (50% accuracy). Optimizes the model through iterative parameter tuning and architecture changes to a final model of 65% accuracy (95% for 2 of the 5 genres).

**RNN - Marvel Character Generator**: An RNN model that takes the text from the Marvel Wiki entries and uses it to generate a backstory for a character. Results vary and still requires better tuning but an interesting introduction!

**MCMC - Breaking the Enigma Code**: Using MCMC algorithm to break the enigma code. Used for creating the Medium article: 

**Data Creation - Jungle Stats per Champion**: Builds a full dataset of each League of Legends Champions average Jungle stats per ranked tier. First creates a dataset of match IDs for each tier, loops through this to find match JSONs then parses JSON to pull & aggregate key information. All performed with parallel processing. 

**Principle Component Analysis**: Exploring techniques to reduce the dimensionality of the 2012 U.S. Army Anthropometric Survey (ANSUR-2). Using predominantly PCA, but a small comparission to the more complex techniques of UMAP and T-SNE is also performed. 

**Principle Component Analysis & Recommendation Engine**: Use PCA to convert data about LoL Champions into 2D space to be used for Euclidean distance "Content-based recommendation" engine. 

**Classification**: Using medical data to classify patients. Transformed using several dimensionality reduction techniques (UMAP/PCA/TSNE) then classified through Supervised Learning (Gaussian Naive Bayes/K-Nearest Neighbors/SVC/Decision Trees), scored on T1 errors through cross-validation to pick optimal model. Further Unsupervised Learning (K-Means / Gaussian Mixture) used to test for further improvements in classification (whether additional categories are beneficial). 

**Data Analysis and API**: Using the Riot API to gather data about LoL player, attempting to prove whether "tilted" players are more likely to lose their next game. Used for creating the Medium article:

**Champion Classification using UMAP and KMeans**: Using Champion statistics alongside UMAP dimensionality reduction to classify LoL champions into four per lane. Used for article and future work (reference to follow)