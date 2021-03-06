# Show libraries 8-11 as beanplots (describe these as 'representative samples')
# source functions and dependencies from 'Group Meeting 2018-06-22 plots.R'
# see also Fig 1C script

setwd('D:/Promoter Design Data')
source('Code/FCS file analysis.R')
setwd('pZEV Library Panel')

fn.key = 'filenames.csv'
require(data.table)
table.key = fread(fn.key)
fns = table.key$Filename

table.key$Construct.orig = table.key$Construct
table.key$Construct = apply(cbind(table.key$Construct, table.key$Concentration, table.key$Replicate),1, function(x) paste0(x, collapse = '_'))
names(fns) = table.key$Construct

files.dat = lapply(fns, load.fromfilename)
files.dat = lapply(files.dat, extract.data, vals = c('mCherry','GFP'))
files.dat = lapply(files.dat, get.rats)
files.dat = lapply(files.dat, drop.outliers, 2e-2)

files.mediansonly = files.dat[which(table.key$Use == 'Median')]
files.dat = files.dat[which(table.key$Use == 'Data')]

lib.names = list()
lib.reps = list()
lib.construct.orig = list()
for(i in 1:length(files.dat)) {
  lib.names[[i]] = rep(table.key$Construct[i], length(files.dat[[i]]))
  lib.reps[[i]] = rep(table.key$Replicate[i], length(files.dat[[i]]))
  lib.construct.orig[[i]] = rep(table.key$Construct.orig[i], length(files.dat[[i]]))
}
lib.names = as.factor(unlist(lib.names))
lib.reps = as.factor(unlist(lib.reps))
lib.construct.orig = as.factor(unlist(lib.construct.orig))

lib.frame = data.frame(Library = lib.names, Activity = unlist(files.dat), Replicate = lib.reps, Construct = lib.construct.orig) 

png(filename = 'D:/Promoter Design Data/Figures/PNGs/S5.png',
    units = 'cm', width = 12, height = 6, res = 600)
p = ggplot(lib.frame, aes(x=Library, y=Activity, fill=Construct)) + geom_violin(color=NA) + theme_bw() + 
  theme(axis.text = element_text(size=12), axis.title = element_text(size=16, face='bold'), legend.position="none",
        axis.title.x=element_blank(), axis.text.x=element_blank(), axis.ticks.x=element_blank())
print(p)
dev.off()



