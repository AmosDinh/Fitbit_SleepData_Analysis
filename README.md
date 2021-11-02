### For potential viewers of the repository:
- The project is not finished yet
- It was created as source for my "presentational skills" talk in university
- It is not a "serious" project, but I rather wanted to see which connections I could find in my sleepdata
- analysis2.ipynb is a "run-on" file 😅


### Dataset
Fitbit personal sleep data
(see this sample)[sleepdata/stages_main_sample.csv]
Nights:
Classic(awake,restless,asleep)  | Detailed (stages)
-------------------|------------------
74 Normal          | 41 Normal
1 Not main sleep (err) | 1 to short (err, because of "1 not main sleep")


  
## Analysis (Not finished)
- Weekday (Detailed)
  - Stage Percentag
  - Time asleep  
  - avg bedtime
  - avg awaketime
  <br><br>
- General (Classic & Detailed)
  - Start - Enddate 
    - Time Asleep
      - Increases by ~ 0.27 h
    - Stage Percentage
    - avg times: similar to taking middle of the slope, but not same!
      - avg bedtime 23.627777777777776 
      - avg wake 8.447150997150999
- Exploring sleepstages further:
  - circardian clock
    - despite having 9hrs to sleep, because i went to bed at 0:44, the body does not allow for much deepsleep(small periods of deepsleep)
  - rem + deep antiprop to light sleep:
    - if you sleep longer does not mean you get more deep and rem sleep
    - body chooses either the one or the other, depending on conditions

- Other
  - How does temperature(Speyer) affect Sleep, Stages, waketime etc?
    - Highest corr between timeasleep and soil 20cm - makes sense, 200cm is too deep, not "the temperature of the actual day"
    - No surprise - sunset affects sleepstarttime, corr = 0.5, temp affects sleepstarttime, corr = 0.5 - but sunset and temp are corr 08 - so unclear which one affects more the sleepstarttime -> Correlation does not tell you if one variable really affects the other - maybe just coincidence, maybe not directly but by sidefactors
    - correlation between time_asleep and temp20cm corr = -0.3
    - I did not know the difference between boden_temp20cm and temp_20cm but correlation sunset/sunrise and the temps tells that the sunlight affects boden_temp20cm more 
  - correlation between light and rem sleep : -0.6839688265149728, between light and deep sleep only - 0.5 -> you are woken up more in the second part of the night, since it is louder, also deep sleep wont allow you to wake up as easily as rem sleep
  - distribution of rem and light sleep per night graph made
  - Does non avg bedtime affect sleep/sleepstages?
  - Alcohol
  - How is sleep and are stages affected when you go to bed late
  - how does abs temperature change of environment affect sleep stages - entry of deep / rem sleep
<br>
<br>

- Conclusion...
  
#### Literature / Sources
- Fitbit sleepdata from Fitbit API
- Temperaturedata of Speyer(ger) https://www.am.rlp.de
- Huberman-Lab Podcasts on Youtube
- The temperature dependence of sleep: https://www.frontiersin.org/articles/10.3389/fnins.2019.00336/full
 
