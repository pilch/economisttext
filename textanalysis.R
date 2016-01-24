library("RSiteCatalyst")
library("RTextTools") 
library(MVA)
library(tm)

setwd('/Users/dreidpilch/Dropbox/PersonalWebsite2/Economist Collaboration')
R <- read.csv("TDM4.csv",header=TRUE,sep=',')
authors <- as.matrix(read.table("authnames.txt",header=FALSE,sep=','))
#ind <- which(authors=="Peter Nijkamp")
#authors = authors[-ind]
cols = which(names(R)=="und"|names(R)=="der"|names(R)=="la")
r <- R[,-cols]

#Most common words
vocab <- data.frame(authors,wordcount=rowSums(r))
vocab[order(-vocab$wordcount),]
mean(vocab$wordcount)


#Vocabulary size by economist (total number of unique words said)
vocab <- data.frame(authors,wordcount=rowSums((r>0)))
vocab[order(-vocab$wordcount),]
mean(vocab$wordcount)

#Keep the top cutoff words for each economist
cutoff <- 1000

for(i in 1:length(r[,1])) {
	
	vocab <- r[i,]
	c <- as.numeric(sort(vocab,decreasing=TRUE)[cutoff])
	r[i,] <- ((r[i,]>=c)*1)*r[i,]
	print(i)
	
}

#Check total number of words said by each economist
ct <- data.frame(authors,count=rowSums(r))
ct[order(-ct$count),]

#Normalize by document size
r <- r/rowSums(r)

#Create the tf matrix, using augmented frequency normalization to control for longer documents
tf <- as.matrix(r)

#Augmented frequency normalization
a <- 0.4
tf <- (a + (1-a)*(tf/apply(tf,1,max)))*((tf>0)*1)

#Binary frequency normalization
#tf <- (tf>0)*1

#Log normalization
#tf <- log(1+tf)

#Binary normalization - not a good way to do it when there's lots of variance in the number
#of terms each author has written
binary <- (tf>0)*1

idf <- log(nrow(tf)/colSums(binary))

tfidf <- tf %*% diag(idf)
tfidf.frame <- data.frame(tfidf)
names(tfidf.frame) <- names(r)
pca = prcomp(tfidf.frame)
lsa = pca$rotation
signif(sort(lsa[,1],decreasing=TRUE)[1:30],2)
signif(sort(lsa[,1],decreasing=FALSE)[1:30],2)
signif(sort(lsa[,2],decreasing=TRUE)[1:30],2)
signif(sort(lsa[,2],decreasing=FALSE)[1:30],2)
signif(sort(lsa[,3],decreasing=TRUE)[1:30],2)
signif(sort(lsa[,3],decreasing=FALSE)[1:30],2)

pca1 <- data.frame(authors,pca1=pca$x[,1])
pca1[order(-pca1$pca1	),]

words <- names(sort(lsa[,2],decreasing=TRUE)[1:30])

plot(pca$x[,1:2])
identify(pca$x[,1],pca$x[,2],authors)

#Weightings on PC1 and PC2, by author
comps <- data.frame(authors=authors,pc1 = pca$x[,1],pc2 = pca$x[,2])
names(comps)[1] <- "authors"
comps[order(-comps$pc1),]

#Test what Peter Nijkamp talks about
toppc1 <- names(signif(sort(lsa[,1],decreasing=TRUE)[1:30],2))
ind <- which(authors=="Peter Nijkamp")
log(r[ind,toppc1]/rowSums(r[ind,]))
log(colMeans(r[-ind,toppc1])/sum(r[-ind,]))

cosine <- function(x,y) {
	return( crossprod(x,y)/sqrt(crossprod(x)*crossprod(y)) )
}

k <- nrow(tfidf)
C <- matrix(NA,k,k)

for(i in 1:k) {
	for (j in 1:k) {
		C[i,j] <- cosine(tfidf[i,],tfidf[j,])
	}
}

Cosines <- data.frame(C,row.names=authors,col.names=authors)
m1 <- apply(C,1,function(x) which(max((x<1)*x)==x))
m2 <- apply(C,1,function(x) max((x<1)*x))
M <- data.frame("author" = authors[,1],"closestpair" = authors[m1],"cosine" = m2)
M[order(-M$cosine),]
write.csv(Cosines,"Cosines.csv")


