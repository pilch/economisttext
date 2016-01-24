library("RSiteCatalyst")
library("RTextTools") 
library(MVA)
library(tm)

setwd("/Users/dreidpilch/Dropbox/PersonalWebsite2/economists")
r <- read.csv("TDM.csv",header=TRUE,sep=',')
authors <- as.matrix(read.table("authnames.txt",header=FALSE,sep=','))

#Most common words
vocab <- data.frame(authors,wordcount=rowSums(r))
vocab[order(-vocab$wordcount),]
mean(vocab$wordcount)

#Vocabulary size by economist (total number of unique words said)
vocab <- data.frame(authors,wordcount=rowSums((r>0)))
vocab[order(-vocab$wordcount),]
mean(vocab$wordcount)

#Check total number of words said by each economist
ct <- data.frame(authors,count=rowSums(r))
ct[order(-ct$count),]

#Create the tf matrix
tf <- as.matrix(r)

#Augmented frequency normalization on the tf matrix
a <- 0.4
tf <- (a + (1-a)*(tf/apply(tf,1,max)))*((tf>0)*1)

#Create the idf matrix
binary <- (tf>0)*1
idf <- log(nrow(tf)/colSums(binary))

#Create the tf-idf matrix
tfidf <- tf %*% diag(idf)
tfidf.frame <- data.frame(tfidf)
names(tfidf.frame) <- names(r)

#Principal components on the tf-idf matrix
pca = prcomp(tfidf.frame)
lsa = pca$rotation

#Check the words with most positive and negative projections on first two prin comps
signif(sort(lsa[,1],decreasing=TRUE)[1:30],2)
signif(sort(lsa[,1],decreasing=FALSE)[1:30],2)
signif(sort(lsa[,2],decreasing=TRUE)[1:30],2)
signif(sort(lsa[,2],decreasing=FALSE)[1:30],2)

#Sort by author weighting on first pc
pca1 <- data.frame(authors,pca1=pca$x[,1])
pca1[order(-pca1$pca1	),]

#Plot authors by weighting on first and second principal components
plot(pca$x[,1:2])
identify(pca$x[,1],pca$x[,2],authors)

#Weightings on PC1 and PC2, by author
comps <- data.frame(authors=authors,pc1 = pca$x[,1],pc2 = pca$x[,2])
names(comps)[1] <- "authors"
comps[order(-comps$pc1),]

#Cosine function to determine cosine between author texts
cosine <- function(x,y) {
	return( crossprod(x,y)/sqrt(crossprod(x)*crossprod(y)) )
}

k <- nrow(tfidf)
C <- matrix(NA,k,k)

#Create the cosine matrix
for(i in 1:k) {
	for (j in 1:k) {
		C[i,j] <- cosine(tfidf[i,],tfidf[j,])
	}
}

#Write the cosine matrix to csv file
Cosines <- data.frame(C,row.names=authors,col.names=authors)
write.csv(Cosines,"Output/cosines.csv")

#For each author, find the author with the highest cosine
m1 <- apply(C,1,function(x) which(max((x<1)*x)==x))
m2 <- apply(C,1,function(x) max((x<1)*x))
M <- data.frame("author" = authors[,1],"closestpair" = authors[m1],"cosine" = m2)
M[order(-M$cosine),]

