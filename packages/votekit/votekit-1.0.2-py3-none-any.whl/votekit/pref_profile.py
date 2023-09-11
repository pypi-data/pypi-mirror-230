import csv
from fractions import Fraction
import pandas as pd
from pydantic import BaseModel, validator
from typing import Optional

from .ballot import Ballot


class PreferenceProfile(BaseModel):
    """
    PreferenceProfile class, contains ballots and and candidates for a
        given eleciton

    **Attributes**

    `ballots`
    :   list of `Ballot` objects

    `candiates`
    :   list of candidates

    **Methods**
    """

    ballots: list[Ballot] = []
    candidates: Optional[list] = None
    df: pd.DataFrame = pd.DataFrame()

    @validator("candidates")
    def cands_must_be_unique(cls, candidates: list) -> list:
        if not len(set(candidates)) == len(candidates):
            raise ValueError("all candidates must be unique")
        return candidates

    def get_ballots(self) -> list[Ballot]:
        """
        Returns list of ballots
        """
        return self.ballots

    def get_candidates(self) -> list:
        """
        Returns list of unique candidates
        """
        unique_cands: set = set()
        for ballot in self.ballots:
            unique_cands.update(*ballot.ranking)

        return list(unique_cands)

    # can also cache
    def num_ballots(self) -> Fraction:
        """
        Counts number of ballots based on assigned weight

        Returns:
            Number of ballots cast
        """
        num_ballots = Fraction(0)
        for ballot in self.ballots:
            num_ballots += ballot.weight

        return num_ballots

    def to_dict(self, standardize: bool) -> dict:
        """
        Converts ballots to dictionary with rankings (keys) and the
        corresponding total weights (values)

        Returns:
            A dictionary with with ranking (keys) and corresponding total \n
            weights (values)
        """
        num_ballots = self.num_ballots()
        di: dict = {}
        for ballot in self.ballots:
            rank_tuple = tuple(next(iter(item)) for item in ballot.ranking)
            if standardize:
                weight = ballot.weight / num_ballots
            else:
                weight = ballot.weight
            if rank_tuple not in di.keys():
                di[rank_tuple] = weight
            else:
                di[rank_tuple] += weight
        return di

    class Config:
        arbitrary_types_allowed = True

    def to_csv(self, fpath):
        """
        Saves Preference Profile to CSV
        Args:
            fpath (str): path to the saved csv
        """
        with open(fpath, "w", newline="") as csvfile:
            fieldnames = ["weight", "ranking"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for ballot in self.ballots:
                writer.writerow({"weight": ballot.weight, "ranking": ballot.ranking})

    def _create_df(self) -> pd.DataFrame:
        """
        Creates DF for display and building plots
        """
        weights = []
        ballots = []
        for ballot in self.ballots:
            part = []
            for ranking in ballot.ranking:
                for cand in ranking:
                    if len(ranking) > 2:
                        part.append(f"{cand} (Tie)")
                    else:
                        part.append(cand)
            ballots.append(tuple(part))
            weights.append(int(ballot.weight))

        df = pd.DataFrame({"Ballots": ballots, "Weight": weights})
        # df["Ballots"] = df["Ballots"].astype(str).str.ljust(60)
        df["Voter Share"] = df["Weight"] / df["Weight"].sum()
        # fill nans with zero for edge cases
        df["Voter Share"] = df["Voter Share"].fillna(0.0)
        # df["Weight"] = df["Weight"].astype(str).str.rjust(3)
        return df.reset_index(drop=True)

    def head(
        self, n: int, percents: Optional[bool] = False, totals: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        Displays top-n ballots in profile based on weight

        Args:
            n: Number of ballots to view
            percents: If True, show voter share for a given ballot
            totals: If true, show total values for Voter Share and Weight

        Returns:
            A dataframe with top-n ballots
        """
        if self.df.empty:
            self.df = self._create_df()

        df = (
            self.df.sort_values(by="Weight", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )

        if totals:
            df = _sum_row(df)

        if not percents:
            return df.drop(columns="Voter Share")

        return df

    def tail(
        self, n: int, percents: Optional[bool] = False, totals: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        Displays bottom-n ballots in profile based on weight

        Args:
            n: Number of ballots to view
            percents: If True, show voter share for a given ballot
            totals: If true, show total values for Voter Share and Weight

        Returns:
            A dataframe with bottom-n ballots
        """
        if self.df.empty:
            self.df = self._create_df()

        df = (
            self.df.sort_values(by="Weight", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )
        if totals:
            df = _sum_row(df)

        if not percents:
            return df.drop(columns="Voter Share")

        return df

    def __str__(self) -> str:
        # Displays top 15 cast ballots or entire profile

        if self.df.empty:
            self.df = self._create_df()

        if len(self.df) < 15:
            return self.head(n=len(self.df)).to_string(index=False, justify="justify")

        return self.head(n=15).to_string(index=False, justify="justify")

    # set repr to print outputs
    __repr__ = __str__

    def condense_ballots(self):
        """
        Groups ballots by rankings and updates weights
        """
        class_vector = []
        seen_rankings = []
        for ballot in self.ballots:
            if ballot.ranking not in seen_rankings:
                seen_rankings.append(ballot.ranking)
            class_vector.append(seen_rankings.index(ballot.ranking))

        new_ballot_list = []
        for i, ranking in enumerate(seen_rankings):
            total_weight = 0
            for j in range(len(class_vector)):
                if class_vector[j] == i:
                    total_weight += self.ballots[j].weight
            new_ballot_list.append(
                Ballot(ranking=ranking, weight=Fraction(total_weight))
            )
        self.ballots = new_ballot_list

    def __eq__(self, other):
        if not isinstance(other, PreferenceProfile):
            return False
        self.condense_ballots()
        other.condense_ballots()
        for b in self.ballots:
            if b not in other.ballots:
                return False
        for b in self.ballots:
            if b not in other.ballots:
                return False
        return True


def _sum_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes sum total for weight and voter share column
    """
    sum_row = {
        "Ballot": "",
        "Weight": df["Weight"].sum(),
        "Voter Share": df["Voter Share"].sum(),
    }

    df.loc["Totals"] = sum_row  # type: ignore

    return df.fillna("")
