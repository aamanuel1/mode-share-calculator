# mode_share.py
# Aaron Manuel
# Group 35
# bitShiftLeft
#
# A command-line/terminal-based application for computing and printing statistics 
# based on transportation mode share for the City of Calgary.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ModeShare:
    """A class that merges and joins some Mode Share data and a key matching communities with sectors from the City of Calgary, 
    prompts for user input, and then does some data analysis with them. The attributes are instantiated with None type and filled
    as needed during the course of the analysis.
    
    Attributes:
        mode_share_2011: 2011 Mode Share DataFrame for use in merging.
        mode_share_2014: 2014 Mode Share from Excel for use in merging.
        mode_share_2016: 2016 Mode Share imported for use in merging.
        communities_by_ward: The key that contains the community-sector connection, also includes other indices for further analysis.
        mode_share_data: The merged mode share data (2011, 2014, 2016 and communities_by_ward).
        planning_sector_list: Pandas index acting as a list for the input checking when the user is inputting the Planning Sector.
        planning_sector_user: The string that contains the desired Sector for analysis.
        travel_mode_list: Pandas index acting as a list for input checking on the 2nd user input (travel mode)
        travel_mode_user: String that contains the desired mode for analysis.

    """
    def __init__(self):
        self.mode_share_2011 = None
        self.mode_share_2014 = None
        self.mode_share_2016 = None
        self.communities_by_ward = None
        self.mode_share_data = None
        self.planning_sector_list = None
        self.planning_sector_user = None
        self.travel_mode_list = None
        self.travel_mode_user = None


    def prepare_dataframe(self):
        """Prepares the dataframe based on data from the City of Calgary on the transportation mode share for each neighbourhood.
        
        Arguments/Parameters:
            No Arguments.

        Returns: 
            No returns.
        
        """
        # Bring in the Excel files for the dataframes
        # First get the key for communities to sector, ward etc, then get the 2011 mode share file.
        self.communities_by_ward = pd.read_excel("City of Calgary Mode Share\Communities_by_Ward.xlsx", index_col = [3,2,1,0,4,5,6], skipfooter = 7)
        raw_mode_share_2011 = pd.read_excel("City of Calgary Mode Share\Civic_census_2011_-_Modes_of_Travel_to_Work.xlsx", index_col = [0, 1, 2], skipfooter = 5)

        # Join the data so that the key is joined on the left, and set the index to the key, communities_by_ward. Left join used due to mismatch in length, may be due to neighbourhood name changes, will investigate later.
        mode_share_data_join_1 = self.communities_by_ward.join(raw_mode_share_2011, how = 'left').set_index(self.communities_by_ward.index)

        # To avoid the warning that we're doing a join on multiple indices, we MultiIndex from product with the key and the 2011 data joined so everything matches.
        columns_2011 = pd.MultiIndex.from_product([['2011'], mode_share_data_join_1.columns], names = ['Year', 'Travel Mode'])
        self.mode_share_2011 = pd.DataFrame(mode_share_data_join_1.values, columns = columns_2011, index = mode_share_data_join_1.index)
        
        # Get the 2014 data and add the MultiIndex for columns by using from_product, where 2014 is the year, and the .columns are the Travel Modes. 
        # Then reform everything with .values, the columns_2014 object and .index because setting the column index led to NaNs without the reformation.
        raw_mode_share_2014 = pd.read_excel("City of Calgary Mode Share\Civic_census_2014_-_Modes_of_Travel_to_Work.xlsx", index_col = [0, 1, 2], skipfooter = 6)
        columns_2014 = pd.MultiIndex.from_product([['2014'], raw_mode_share_2014.columns], names = ['Year', 'Travel Mode'])
        self.mode_share_2014 = pd.DataFrame(raw_mode_share_2014.values, columns = columns_2014, index = raw_mode_share_2014.index)

        # Join on the previous join. Outer join because the left DataFrame has more info (more newer communities).
        mode_share_data_join_2 = pd.merge(self.mode_share_2011, self.mode_share_2014, left_on = 'Community Code', right_on = 'Community Code', how = 'outer')
        
        # Same thing as above but for 2016.
        raw_mode_share_2016 = pd.read_excel("City of Calgary Mode Share\Civic_census_2016_-_Modes_of_Travel_to_Work.xlsx", index_col = [0, 1, 2], skipfooter = 6)
        columns_2016 = pd.MultiIndex.from_product([['2016'], raw_mode_share_2016.columns], names = ['Year', 'Travel Mode'])
        self.mode_share_2016 = pd.DataFrame(raw_mode_share_2016.values, columns = columns_2016, index = raw_mode_share_2016.index)

        # Have to use set_index because we lost the communities_by_ward index with the joins. Inner join used because we're assuming the Community-Sector key (Communities by Ward) and mode share 2016 are the same.
        mode_share_data_join_3 = pd.merge(mode_share_data_join_2, self.mode_share_2016, left_on = 'Community Code', right_on = 'Community Code', how = 'inner').set_index(self.communities_by_ward.index)

        # Order the data, subject to change.
        self.mode_share_data = mode_share_data_join_3.sort_index(axis = 0, level = [0,1])

        # Get the list of valid mode share while we still have access to the raw data (will be out of scope outside of def.)
        # Remove "Total" by only taking the list not including the last entry (slice from -1 index), as Total is not a valid mode share.
        raw_travel_mode_list = raw_mode_share_2016.columns
        self.travel_mode_list = raw_travel_mode_list[:-1]


    def user_interface(self):
        """Prompts the user for two inputs and checks them for validity before storing and continuing. 
        Asks for a Planning Sector (e.g. CENTRE, WEST, NORTHWEST), and a mode of travel (e.g Drove Alone, Transit)

        Arguments/Parameters:
            No Arguments.

        Returns: 
            No returns.
        
        """
        # Preamble to welcome the user.
        print("\nCity of Calgary Mode Share Analysis (ENSF 592 Final Project)")
        print("************************************************************")

        # Get lists of planning sector and store as list or set.
        planning_sector_community_code = pd.read_excel("City of Calgary Mode Share\Communities_by_Ward.xlsx", index_col = [3], skipfooter = 7)
        self.planning_sector_list = set(planning_sector_community_code.index)

        # Get Sector from user and store, use while and try-except block with raise ValueError to catch non-valid input from the set.
        while(True):
            try:
                print("\nThe following are valid planning sectors. ")
                print(*self.planning_sector_list, sep = ", ")
                planning_sector_user = input("Please enter a planning sector: ")

                if(planning_sector_user in self.planning_sector_list):
                    self.planning_sector_user = planning_sector_user
                    break

                else:
                    raise ValueError("Valid Planning Sector not entered.")

            except ValueError:
                print("You must enter a valid planning sector")


        # Get Travel Mode from user and store, same as above.
        while(True):
            try:
                print("\nThe following are valid travel modes. ")
                print(*self.travel_mode_list, sep = ", ")
                travel_mode_user = input("Please enter a travel mode: ")

                if(travel_mode_user in self.travel_mode_list):
                    self.travel_mode_user = travel_mode_user
                    break

                else:
                    raise ValueError("Valid Travel Mode not entered.")

            except ValueError:
                print("You must enter a travel mode.")



    def mode_share_analysis(self):
        """Performs an analysis on the mode share data formed in prepare_dataframe(). Includes things like an aggregate description of the dataset, 
        Mode share totals and percentages for neighbourhoods in a sector, and other analysis (subject to change or addition)

        Arguments:
            No Arguments.

        Parameters:
            No Parameters.
        
        """
        # Set up Index Slice, and set all_rows to be all 7 row MultiIndexes to slice everything. Set user_sector_rows to slice on what sector the user asked for.
        idx = pd.IndexSlice
        all_rows = idx[:,:,:,:,:,:,:]
        user_sector_rows = idx[self.planning_sector_user,:,:,:,:,:,:]

        # Fill 0 with nan, assuming that no one lived in these neighbourhoods at the time or were being planned. Use inplace so it's not a copy.
        self.mode_share_data.fillna(value = 0, inplace = True)

        # Describe entire dataset (need to do in chunks of years)
        # Have to do IndexSlice for each year in the multiindex.
        print("\n--Aggregate Description of Dataset--\n")
        print("2011 Subset: ")
        print(self.mode_share_data.loc[all_rows, idx['2011', : ]].describe())

        print("\n2014 Subset: ")
        print(self.mode_share_data.loc[all_rows, idx['2014', : ]].describe())

        print("\n2016 Subset: ")
        print(self.mode_share_data.loc[all_rows, idx['2016', : ]].describe())

        # Add percentages for Travel Mode for the requested mode for all 3 years. Show the final result. Fill nans with 0 in place (modify not show copy), assuming that a zero neighbourhood is an empty neighbourhood.
        self.mode_share_data.loc[all_rows, idx['2011', ('% ' + self.travel_mode_user)]] = self.mode_share_data.loc[all_rows, idx['2011', self.travel_mode_user]] / self.mode_share_data.loc[all_rows, idx['2011','Total']]
        self.mode_share_data.loc[all_rows, idx['2014', ('% ' + self.travel_mode_user)]] = self.mode_share_data.loc[all_rows, idx['2014', self.travel_mode_user]] / self.mode_share_data.loc[all_rows, idx['2014','Total']]
        self.mode_share_data.loc[all_rows, idx['2016', ('% ' + self.travel_mode_user)]] = self.mode_share_data.loc[all_rows, idx['2016', self.travel_mode_user]] / self.mode_share_data.loc[all_rows, idx['2016','Total']]
        self.mode_share_data.fillna(value = 0, inplace = True)

        # Print out the total number of people, and percentage of people using that mode.
        print("\n--Number of Persons Travelling by Mode " + self.travel_mode_user + "--")
        print(self.mode_share_data.loc[user_sector_rows, idx[ : , (self.travel_mode_user,'Total')]])

        print("\n--Proportion of Persons Travelling by Mode " + self.travel_mode_user + "--")
        print(self.mode_share_data.loc[user_sector_rows, idx[ : , ('% ' + self.travel_mode_user)]])

        # Are there any neighbourhoods that are developing (eg 0 total)
        print("\n--List of Potential New or Planned Neighbourhoods With zero population--")
        sector_total = self.mode_share_data.loc[user_sector_rows, idx[:, 'Total']]

        # If there are any zeroes in the Total, then slice and mask on the Total being 0. Mask on the .values only otherwise everything will NaN.
        if np.any(sector_total == 0):
            print("\nNeighbourhoods with zero population in any analysis year: ")
            print(sector_total.loc[user_sector_rows, idx[ : , 'Total']][sector_total.values == 0])
        
        # If the sector doesn't have any zero-pop neighbourhoods then tell the user.
        else:
            print("\nNo zero-population neighbourhoods.")
    
        # Groupby Sector and Community Structure to get max and min neighbourhood proportion for the Sector and for the Community Structure.
        # Stack on level 0 will bring the 'Year' into a column so that there isn't a KeyError when querying for things. Aggregate on highest mode share proportion in each neighbourhood
        # on what we're grouping by.
        print("\nMinimum and Maximum Neighbourhood Level Trip Proportions by Sector travelling by mode: " + self.travel_mode_user)
        print(self.mode_share_data.stack(level = 0).groupby('Sector')['% ' + self.travel_mode_user].aggregate([min, max]))
        print("\nMinimum and Maximum Neighbourhood Trip Proportions by Community Structure travelling by mode: " + self.travel_mode_user)
        print(self.mode_share_data.stack(level = 0).groupby('COMM_STRUCTURE')['% ' + self.travel_mode_user].aggregate([min, max]))
        
        # Calculate mode share of requested travel mode for requested sector. Compare to citywide mode share of requested travel mode with a printout and plot.
        sector_requested_travel_mode = self.mode_share_data.loc[user_sector_rows, idx[: , :]].sum(axis=0)
        sector_mode_share_by_year = sector_requested_travel_mode.loc[:, self.travel_mode_user] / sector_requested_travel_mode.loc[:, 'Total']

        citywide_requested_travel_mode = self.mode_share_data.loc[all_rows, idx[: , :]].sum(axis=0)
        citywide_mode_share_by_year = citywide_requested_travel_mode.loc[:, self.travel_mode_user]/citywide_requested_travel_mode.loc[:, 'Total']


        # Form a dataframe on the sector mode share and the citywide mode share and print that to the user.
        sector_citywide_mode_share_compare = pd.DataFrame({'CITYWIDE': citywide_mode_share_by_year, self.planning_sector_user: sector_mode_share_by_year})
        print("\nSector and Citywide Mode Share per Year on Requested Mode: " + self.travel_mode_user)
        print(sector_citywide_mode_share_compare)

        # Make plot comparing the sector to the citywide proportion over time. Save that plot in the folder.
        plt.figure(1)
        plt.plot(sector_citywide_mode_share_compare)
        plt.title("Sector and Citywide mode share on travel mode: " + self.travel_mode_user)
        plt.legend(['CITYWIDE', self.planning_sector_user])
        plt.ylabel('Proportion of Mode Share')
        plt.xlabel('Year')
        plt.savefig("sector_citywide_mode_share_compare")

        # Pivot Table (compare the Sector asked for with all Sectors with the mode share (values), over time (columns))
        # Stack on level 0 (Year) so that it moves to an index to avoid KeyError use np.sum to sum the number of persons total and the number of people using the user inputted mode.
        # Then divide them both to get the mode share proportion over sectors and years.
        print("\nPivot Table - " + self.travel_mode_user + " Proportion by Sector for 2011, 2014, 2016")
        sector_year_pivot_on_user_mode = self.mode_share_data.stack(level = 0).pivot_table(values = (self.travel_mode_user), index = 'Sector', columns = "Year", aggfunc = np.sum ) 
        sector_year_pivot_on_total = self.mode_share_data.stack(level = 0).pivot_table(values = ('Total'), index = 'Sector', columns = "Year", aggfunc = np.sum )

        # Export to Excel and plot other figure. Show the plots at the end.
        sector_year_pivot_mode_share = sector_year_pivot_on_user_mode / sector_year_pivot_on_total
        print(sector_year_pivot_mode_share)
        plt.figure(2, figsize =(10,5))
        plt.plot(sector_year_pivot_mode_share)
        plt.title(self.travel_mode_user + " Proportion by Sector and Year")
        plt.legend(['2011', '2014', '2016'])
        plt.xlabel('Sector')
        plt.ylabel('Proportion of Mode Share')
        plt.savefig("sector_year_pivot_mode_share")

        self.mode_share_data.to_excel("mode_share_data.xlsx")

        plt.show()

        print("\n----------END OF ANALYSIS----------")

        

def main():

    # Form the class and combined dataframe (Stage 2)
    mode_share = ModeShare()
    mode_share.prepare_dataframe()

    # Ask the user for input (Stage 3)
    mode_share.user_interface()

    # Perform the analysis and stuff here (Stage 4) and print out results here of the analysis (Stage 5)
    mode_share.mode_share_analysis()




if __name__ == '__main__':
    main()