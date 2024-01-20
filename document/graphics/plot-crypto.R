d1<-scan("hw-python.txt")
d2<-scan("python.txt")

pdf("AES.pdf")
plot(density(d1), xlim=c(min(d1), max(d2)), col="dark red", lwd=3, main="AES256 encryption: Python+hardware vs pure Python", xlab="Time to encrypt in CBC mode 1024 bytes, ms")
lines(density(d2), lwd=3, col="dark blue")
legend("topright", c("Python and hardware", "Pure Python"), col=c("dark red", "dark blue"), lwd=3, bg='lightblue')
grid(lwd=3)
dev.off()
