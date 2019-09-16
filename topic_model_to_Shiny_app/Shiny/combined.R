#! /usr/bin/Rscript

# server file
# now loading newest dataset
library(methods)
library(tidyr)
library(dplyr)
library(reshape2)
library(tm)
library(slam)
library(utils)
library(stats)
library(shinydashboard)
library(shiny)
library(leaflet)
library(plotly)
library(here)


# loading data
OA_hh <- data.frame(read.csv(here('topic_model_to_Shiny_app','Shiny','static','Leeds_MSOA_2.csv')))

LeedsOA <- geojsonio::geojson_read(here('topic_model_to_Shiny_app','Shiny','static','Leeds_MSOA.geojson'), what = 'sp')

# only first 10 cols are there are no others
LDA_df <- data.frame(read.csv(here('topic_model_to_Shiny_app','data','transformed_data_source.csv'), row.names='X'))

server <- function(input, output, session) {

  observeEvent({
    input$MonYear
    input$topic
    input$rateswitch}, {

      # filter by date
      if(is.null(input$topic)){
        manip_df <- LDA_df[which(LDA_df$Month2 %in% c(input$MonYear[1]:input$MonYear[2])),]
      }else{
        manip_df <- LDA_df[which(LDA_df$Month2 %in% c(input$MonYear[1]:input$MonYear[2]) & LDA_df$Topic_keywords == input$topic),]
      }

      # perform incident counting
      lsoa_count <- as.data.frame(table(unlist(strsplit(as.character(manip_df$MSOA), ','), recursive=FALSE)))

      colnames(lsoa_count) <- c('code','freq')

      # filling in missing lsoa after counting
      '%!in%' <- function(x,y)!('%in%'(x,y))

      # get all output area names
      OA_names <- data.frame(LeedsOA$msoa01cd)

      print('Test if i get here')

      colnames(OA_names) <- c('code')

      missing_df <- data.frame(OA_names$code[OA_names$code %!in% lsoa_count$code], 0)

      colnames(missing_df) <- c('code','freq')

      lsoa_full <- rbind(lsoa_count, missing_df)

      # if the dataframe ever changes the 2nd column selected here changes by the number of columns added/removed
      # must select the strsplit col and CrimeNotes col
      reports <- unnest(manip_df, strsplit(as.character(manip_df$MSOA),','))#[,c(4,11)]

      reports <- reports %>%
        group_by(`strsplit(as.character(manip_df$MSOA), ",")`) %>%
        summarise(CrimeNotes = paste(CrimeNotes, collapse = '<br> <br>'))

      names(reports) <- c('code','CrimeNotes')

      lsoa_full <- left_join(lsoa_full, reports, by = 'code')

      # manipulate depending on count or rate selection
      if(input$rateswitch != 'Counts'){
        lsoa_full$freq <- lsoa_full$freq/OA_hh$Households
      }

      # return final ordered lsoa plus counts
      lsoa_full <- lsoa_full[match(LeedsOA@data$msoa01cd, lsoa_full$code),]


      pal <- colorNumeric(c('white', 'red'), domain = lsoa_full$freq)

      output$mymap <- renderLeaflet({
        leafletOptions(maxZoom = 10)
        leaflet(LeedsOA) %>%
          setView(lat = 53.816497, lng =-1.536751, zoom = 11) %>%
          addTiles() %>%
          addPolygons(data = LeedsOA,
                      stroke = TRUE,
                      color = "black",
                      fillOpacity=0.7,
                      fillColor = ~pal(lsoa_full$freq),
                      dashArray = 2,
                      weight = 0.7,
                      popup = paste(lsoa_full$CrimeNotes)
          ) %>%
          addLegend('bottomright',pal = pal, values = ~lsoa_full$freq,
                    title=as.character(input$rateswitch))
      })

      output$topictext <- renderText(HTML(paste0('<strong>Topic keywords: </strong>',as.character(manip_df$Topic_keywords[1]))))

      print('Runs past leaflet section')
      #### Plot_ly segment

      # perform processing for plot_ly topics over time

      topictime <- manip_df %>%
        group_by(LDA_Topic, Month2) %>%
        summarise(n = n()) %>%
        spread(Month2, n, fill = 0)

      # drop LDA_Topics col
      topictime <- data.frame(topictime)

      topictime[,1] <- NULL

      # transpose dataframe
      topictime <- data.frame(t(topictime))

      # set rows to 1 to 24 month counts
      # unclear this is necessary?
      # TODO: but needs to be able to handle data with missing months etc 
      #topictime <- data.frame(topictime, row.names = c(input$MonYear[1]:input$MonYear[2]))

      # create a dataframe of ordered topics for correct alignment and column naming
      df1 <- unique(manip_df[,c('LDA_Topic','Topic_keywords')])

      df1 <- df1[order(df1$LDA_Topic),]

      # set column names as topic keywords
      colnames(topictime) <- df1$Topic_keywords

      # add month year codes
      topictime$Month2 <- tibble::rownames_to_column(topictime, 'Month2')

      # convert data into tall format for graphing
      data.tall <- melt(topictime,
                        variable.name = 'Topic',
                        value.names = 'count',
                        id.vars = ('Month2'))

      # x axis specification
      axaxis <- list(
        title = 'Months',
        tick0 = 1,
        dtick = 1
        #ticklen = 25,
        #ticklen
      )

      print('Runs past plot_ly data manip')
      # actual plot_ly output

      output$topicstimeplot <- renderPlotly(
        plot_ly(data.tall, x = ~Month2,
                y= ~value,
                type = 'scatter',
                name = ~Topic,
                mode = 'lines',
                text = ~Topic,
                hoverinfo = 'text+x+y') %>%
          layout(title = "Topics over time",
                 xaxis = axaxis,
                 yaxis = list (title = "Counts",
                               showline = TRUE),
                 showlegend = FALSE)
      )

      print('Runs past plot_ly plot')
      #### section for NLP computation of words within reports
      ### this requires tm and slam packages (already loaded)

      # select out tokens
      tokens <- manip_df$Tokens

      # grep removal of square brackets, commas, and single quote marks
      tokens <- gsub("\\[|\\]|'|,",'',tokens)

      # creation of corpus using tm
      corpus <- Corpus(VectorSource(tokens))

      # control settings for documentTermMatrix
      # set lower bound (no words that occur in less than 5% of docs)
      minDocFreq <- length(corpus) * 0.05

      # set upper bound (no words that occur in more than 80% of docs)
      maxDocFreq <- length(corpus) * 0.8

      # create DocumentTermMatrix
      DTM <- DocumentTermMatrix(corpus, control = list(bounds = list(global = c(minDocFreq, maxDocFreq))))

      observeEvent({input$submit_text},{
        # lets build in a level of reactivity so a user can specify a key word
        terms <- as.character(input$keyword_text)

        if (terms == ""){

          reduced_DTM <- as.matrix(DTM)

        } else{
          # perform quick regex formatting to create list of strings

          terms <- tolower(trimws(unlist(strsplit(terms, ","))))

          accepted_terms <- list()

          rejected_terms <- list()

          for (x in terms){
            if (x %in% DTM$dimnames$Terms){
              accepted_terms[[length(accepted_terms)+1]] <- x
            }else{
              rejected_terms[[length(rejected_terms)+1]] <- x
            }
          }

          # ensure DTM has acceptable terms to slice
          # if not return whole DTM
          if (length(accepted_terms) != 0){
            reduced_DTM <- as.matrix(DTM[,unlist(accepted_terms)])
          }else{
            reduced_DTM <- as.matrix(DTM)
          }

          if (length(rejected_terms) != 0) {
            output$rejected_terms <- renderUI(HTML("<font color =\"#FF0000\"><b>",'The following terms were not found:',paste0(unlist(rejected_terms), collapse=' '),"</b></font>"))
          }


        }
        print('split 1')
        counts_per_decade <- aggregate(reduced_DTM, by = list(Month2 = manip_df$Month2), sum)
        print('split 2')
        wordcountsdecade.tall <- melt(counts_per_decade,
                                      variable.name = 'Word',
                                      value.names = 'count',
                                      id.vars = ('Month2'))
        print('runs past topic model bit')

        # actual plotly call to shiny ui
        # x axis already defined in previous plot
        output$wordbymonth <- renderPlotly(
          plot_ly(wordcountsdecade.tall, x = ~Month2,
                  y= wordcountsdecade.tall$value,
                  type = 'scatter',
                  name = wordcountsdecade.tall$Word,
                  mode = 'lines',
                  text = wordcountsdecade.tall$Word,
                  hoverinfo = 'text+x+y') %>%
            layout(title = "Word occurence over time",
                   xaxis = axaxis,
                   yaxis = list (title = "Counts",
                                 showline = TRUE),
                   showlegend = FALSE)
        )
      })

    })
}

### UI section ###

header <-  dashboardHeader(title = 'LDA Viewer')

# main page panel
body <- dashboardBody(

  # create a row for controls
  fluidRow(
    box(# select topic
      selectizeInput('topic','Select a LDA topic:',
                     choices = LDA_df$Topic_keywords,
                     selected = NULL,
                     options = list(create = TRUE),
                     multiple = TRUE),

      radioButtons('rateswitch','Counts or Rates: ',
                   choices = c('Counts', 'Rate (counts/hh)'),
                   selected = 'Counts')
    ),
    box(# time slider
      sliderInput('MonYear','Select a Month over 1 year:',
                  min = min(LDA_df$Month2),
                  max = max(LDA_df$Month2),
                  value = c(1,12), step = unique(LDA_df$Month2),
                  animate = animationOptions(interval = 3000, loop = TRUE)
      )
    )
  ),
  fluidRow(
    # map column within row
    column(width = 8,
           box(width = NULL, solidHeader = TRUE,
               leafletOutput("mymap", height = 800))
    ),
    # column for other plots
    column(width = 4,
           box(width = NULL,
               solidHeader = FALSE,
               plotlyOutput('topicstimeplot')),
           box(width = NULL,
               solidHeader = FALSE,
               # text input section
               textInput(inputId = 'keyword_text', label = 'Enter keyword(s):', value = ""),
               htmlOutput(outputId = 'rejected_terms'),
               actionButton(inputId = 'submit_text', label = 'Submit'),
               plotlyOutput("wordbymonth")
           )
    )
  )
)


ui <- dashboardPage(
  header,
  dashboardSidebar(disable = TRUE),
  body)

runApp(list(ui = ui, server = server), launch.browser = TRUE)
