import numpy as np
import pandas as pd
import networkx as nx

import matplotlib.pyplot as plt

from random import shuffle

from itertools import zip_longest

from scipy.stats import gamma, expon, norm, multinomial, dirichlet
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import matrix_power

from sklearn.preprocessing import minmax_scale

from tqdm import tqdm

class Metadata:
    def __init__(self, n_users:int, n_vendors:int, n_products:int, 
                 countries:list[str], categories:dict[list[str]], mean_price_category:dict):
        
        self.n_users = n_users
        self.n_vendors = n_vendors
        self.n_products = n_products
            
        self.countries = countries
        self.categories = categories
        self.mean_price_category = mean_price_category
        self.n_countries = len(countries)

        self.users = self.gen_metadata_users(self.n_users)
        self.vendors = self.gen_metadata_vendors(self.n_vendors)
        self.products = self.gen_metadata_products(self.n_products)
        self.stock = self.gen_metadata_stock(self.products, self.n_vendors)

    def gen_metadata_users(self, n_users:int):
        df = pd.DataFrame()
        df["country"] = self.countries
        df["age_scale_males"] = np.abs(norm(loc=6,scale=2).rvs(self.n_countries))
        df["age_scale_females"] = np.abs(norm(loc=6,scale=2).rvs(self.n_countries))
        p = dirichlet(alpha=np.ones(self.n_countries)).rvs(1).reshape(-1)
        df[f"total_users"] = multinomial(n_users,p).rvs(1).reshape(-1)
        df["gender_prop"] = norm(0.5,0.1).rvs(self.n_countries)
        df["n_males"] = (df["gender_prop"] * df[f"total_users"]).astype(int)
        df["n_females"] = df[f"total_users"] - df["n_males"]
        return df

    def gen_metadata_vendors(self, n_vendors:int):
        df = pd.DataFrame()
        df["country"] = self.countries
        df["age_scale_males"] = np.abs(norm(loc=6,scale=2).rvs(self.n_countries))
        df["age_scale_females"] = np.abs(norm(loc=6,scale=2).rvs(self.n_countries))
        p = dirichlet(alpha=np.ones(self.n_countries)).rvs(1).reshape(-1)
        df[f"total_vendors"] = multinomial(n_vendors,p).rvs(1).reshape(-1)
        df["gender_prop"] = norm(0.5,0.1).rvs(self.n_countries)
        df["n_males"] = (df["gender_prop"] * df[f"total_vendors"]).astype(int)
        df["n_females"] = df[f"total_vendors"] - df["n_males"]
        return df


    def gen_metadata_products(self, n_products:int):
        df = pd.DataFrame()
        values = []
        for category in self.categories.keys():
            param = self.mean_price_category[category]/20
            costs = gamma(a=param,loc=0,scale=20).rvs(len(self.categories[category]))
            values += list(zip_longest(
                [category],
                self.categories[category],
                costs,  
                fillvalue=category
            ))
        df[["category","subcategory","mean_cost"]] = values
        p = dirichlet(alpha=np.ones(len(df))).rvs(1).reshape(-1)
        df["n_products"] = multinomial(n_products,p).rvs(1).reshape(-1).astype(int)
        return df

    def gen_metadata_stock(self, metadata_products:pd.DataFrame, n_vendors:int):
        metadata_stock = pd.DataFrame()
        metadata_stock["vendor_id"] = np.arange(n_vendors)
        for category in metadata_products["category"].unique():
            metadata_stock[category] = dirichlet(np.ones(n_vendors)).rvs(1).reshape(-1)
        return metadata_stock




class Store:
    def __init__(self, n_users:int, n_vendors:int, n_products:int, 
                 countries:list[str], categories:dict[list[str]], mean_price_category:dict):

        self.metadata = Metadata(n_users, n_vendors, n_products,
                                 countries, categories, mean_price_category)

        self.users = self.gen_users(self.metadata.users)
        self.vendors = self.gen_vendors(self.metadata.vendors)
        self.products = self.gen_products(self.metadata.products)
        self.stock = self.gen_stock(self.metadata.stock, self.metadata.products, self.products)


    def gen_users(self, metadata_users: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for i in range(len(metadata_users)):
            country, scale_m, scale_f, total, _, n_m, n_f = metadata_users.loc[i]
            if total > 0:
                sex = n_m * ["M"] + n_f * ["F"]
                ages = np.hstack([
                    expon(loc=18, scale=scale_m).rvs(n_m),
                    expon(loc=18, scale=scale_f).rvs(n_f)
                ]).astype(int).tolist()
                loc = [country] * total
                rows.extend(zip(sex, ages, loc))
        shuffle(rows)
        df = pd.DataFrame(rows, columns=["sex", "age", "location"]).reset_index()
        df["user_id"] = np.arange(1,len(df)+1)
        df = df[["user_id","sex", "age", "location"]]
        return df

    def gen_vendors(self, metadata_vendors: pd.DataFrame) -> pd.DataFrame:
        rows = []
        posible_stars = [1, 2, 3, 4, 5]
        p = [0.05, 0.1, 0.25, 0.3, 0.3]
        for i in range(len(metadata_vendors)):
            country, scale_m, scale_f, total, _, n_m, n_f = metadata_vendors.loc[i]
            if total > 0:
                stars = np.random.choice(posible_stars, p=p, size=total)
                sex = n_m * ["M"] + n_f * ["F"]
                ages = np.hstack([
                    expon(loc=18, scale=scale_m).rvs(n_m),
                    expon(loc=18, scale=scale_f).rvs(n_f)
                ]).astype(int).tolist()
                loc = [country] * total
                rows.extend(zip(sex, ages, loc, stars))
        shuffle(rows)
        df = pd.DataFrame(rows, columns=["sex", "age", "location", "stars"])
        df["vendor_id"] = np.arange(1,len(df)+1)
        df = df[["vendor_id", "sex", "age", "location", "stars"]]
        return df

    def gen_products(self, metadata_products: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for i in range(len(metadata_products)):
            category, subcategory, mean_cost, total = metadata_products.loc[i]
            if total > 0:
                costs = (
                    gamma(a=mean_cost / 2, scale=2).rvs(total).astype(int)
                    + np.random.choice(
                        [0.0, 0.50, 0.99],
                        p=[0.35, 0.2, 0.45],
                        size=total
                    )
                ).astype(float)
                for c, sc, cost in zip([category]*total, [subcategory]*total, costs):
                    rows.append((c, sc, cost))
        shuffle(rows)
        df = pd.DataFrame(rows, columns=["category", "subcategory", "cost"]).reset_index()
        df["product_id"] = np.arange(1,len(df)+1)
        df = df[["product_id", "category", "subcategory", "cost"]]
        return df

    def gen_stock(self, metadata_stock: pd.DataFrame, metadata_products: pd.DataFrame, df_products: pd.DataFrame) -> pd.DataFrame:
        product_id_by_cat_and_subcat = {}
        for category in self.metadata.categories.keys():
            product_id_by_cat_and_subcat[category] = {}
            for subcategory in self.metadata.categories[category]:
                indices = df_products[
                    (df_products["category"] == category)
                    & (df_products["subcategory"] == subcategory)
                ].index.to_numpy()
                product_id_by_cat_and_subcat[category][subcategory] = indices + 1

        rows = []
        for i in range(len(metadata_products)):
            category, subcategory, mean_cost, total = metadata_products.loc[i]
            if total > 0:
                p = metadata_stock[category]
                stock_dist = multinomial(total, p).rvs(1).reshape(-1)
                non_zero_indices = np.argwhere(stock_dist != 0).reshape(-1)
                vendor_id = (metadata_stock.loc[non_zero_indices, "vendor_id"].to_numpy() + 1)
                available_units = stock_dist[non_zero_indices]
                product_id = product_id_by_cat_and_subcat[category][subcategory]
                for v, p_id, units in zip(vendor_id, product_id, available_units):
                    rows.append((v, p_id, units))
        shuffle(rows)
        df = pd.DataFrame(rows, columns=["vendor_id", "product_id", "available_units"])
        return df

    def get_query_users(self) -> str:
            values = ",".join(
                f"({row.user_id},'{row.sex}',{row.age},'{row.location}')"
                for row in self.users.itertuples(index=False)
            )
            return f"INSERT INTO users (user_id, sex, age, location) VALUES {values};"

    def get_query_vendors(self) -> str:
        values = ",".join(
            f"({row.vendor_id},'{row.sex}',{row.age},'{row.location}',{row.stars})"
            for row in self.vendors.itertuples(index=False)
        )
        return f"INSERT INTO vendors (vendor_id, sex, age, location, stars) VALUES {values};"

    def get_query_products(self) -> str:
        values = ",".join(
            f"({row.product_id},'{row.category}','{row.subcategory}',{row.cost})"
            for row in self.products.itertuples(index=False)
        )
        return f"INSERT INTO Products (product_id, category, subcategory, cost) VALUES {values};"

    def get_query_stock(self) -> str:
        values = ",".join(
            f"({row.vendor_id},{row.product_id},{row.available_units})"
            for row in self.stock.itertuples(index=False)
        )
        return f"INSERT INTO Stock (vendor_id, product_id, available_units) VALUES {values};"


class StoreModel(Store):
    def __init__(self, n_users:int, n_vendors:int, n_products:int,
                 countries:list[str], categories:dict[list[str]], mean_price_category:dict,
                 initial_sex_prob:dict):
        
        super().__init__(n_users, n_vendors, n_products, countries, categories, mean_price_category)
        
        self.state: pd.DataFrame
        self.orders: pd.DataFrame
        self.stock_updated: pd.DataFrame

        self.initial_cat_prob: pd.DataFrame
        self.initial_sub_prob: pd.DataFrame
        self.initial_sex_prob: dict
        self.initial_loc_prob: pd.DataFrame
        self.initial_age_prog: pd.DataFrame

        self.transition_matrix: lil_matrix
        self.graph: nx.DiGraph

        self.decoder_leafs: dict
        self.decoder_data: dict
        self.cat_indices: dict
        self.subcat_indices: dict

        self.__start_indices: np.ndarray
        self.__initial_sex_prob: dict = initial_sex_prob

        self.reset_state()
        self.reset_initial_prob()
        self.build_model()

    def reset_store(self):
        super().__init__(self, self.n_users, self.n_vendors, self.n_products,
                         self.countries, self.categories, self.mean_price_category)
        
        self.reset_state()
        self.reset_initial_prob()
        self.build_model()

    def reset_initial_prob(self):
        self.initial_cat_prob = self.get_initial_cat_prob(self.state)
        self.initial_sub_prob = self.get_initial_sub_prob(self.state)
        self.initial_sex_prob = self.get_initial_sex_prob()
        self.initial_loc_prob = self.get_initial_loc_prob()
        self.initial_age_prob = self.get_initial_age_prob()

    def reset_state(self):
        state = self.stock.merge(self.vendors,on="vendor_id").merge(self.products,on="product_id").copy()

        for cat in state["category"].unique():
            for subcat in state.loc[state["category"]==cat,"subcategory"].unique():
                mask = (state["category"] == cat) & ((state["subcategory"] == subcat))
                state.loc[mask,"interest"] = (
                    minmax_scale(-state.loc[mask,"cost"]) + 
                    minmax_scale(state.loc[mask,"stars"]) +
                    norm(0,0.2).rvs(mask.sum())
                )

        state.sort_values(["category","subcategory","interest"],ascending=False,inplace=True)
        self.state = state

    def get_prob_cat(self, state:pd.DataFrame):
        prob = np.copy(self.initial_cat_prob)
        df = state[["category","available_units"]].groupby("category").sum().reset_index()
        mask = df["available_units"].values > 0
        if (~mask).any():
            prob[~mask] = 0
            prob[mask] /= prob.sum()
        return prob    
        
    def get_prob_subcat(self, state:pd.DataFrame, cat:str):
        prob = np.copy(self.initial_sub_prob[cat])
        df = state.loc[state["category"]==cat,["subcategory","available_units"]].groupby("subcategory").sum().reset_index()
        mask = df["available_units"].values > 0
        if (~mask).any():
            prob[~mask] = 0
            prob[mask] /= prob.sum() 
        return prob     

    def get_prob_sex(self, cat:str):
        male_prob = self.initial_sex_prob[cat]
        prob = np.array([male_prob, 1-male_prob])
        return prob

    def get_prob_loc(self, sex:str):
        return self.initial_loc_prob["posterior_"+("male" if sex=="M" else "female")].values

    def get_prob_age(self, sex:str, loc:str):
        mask = (self.initial_age_prob["sex"]==sex)&(self.initial_age_prob["location"]==loc)
        prob = self.initial_age_prob.loc[mask,"posterior"].values
        return prob

    
    def get_initial_cat_prob(self, state):
        n_cats = state["category"].nunique()
        initial_cat_prob = np.full((n_cats,), fill_value=1/n_cats)
        return initial_cat_prob

    def get_initial_sub_prob(self, state):
        initial_sub_prob = {}
        for cat in state["category"].unique():
            n_sub = state.loc[state["category"]==cat,"subcategory"].nunique()
            initial_sub_prob.update({cat: np.full((n_sub,), fill_value=1/n_sub)})
        return initial_sub_prob

    def get_initial_sex_prob(self):
        initial_sex_prob = self.__initial_sex_prob
        return initial_sex_prob
    
    def get_initial_loc_prob(self):
        locs = np.sort(self.users["location"].unique())
        initial_loc_prob = pd.DataFrame({
            "location": locs,
            "prior": dirichlet(5*np.ones(len(locs))).rvs().reshape(-1)
        }).merge(
            (    pd.concat([self.users["location"],self.users["sex"]=="M"],axis=1)
                .rename(columns={"sex":"likelihood_male"})
                .groupby("location")
                .mean()
                .reset_index()
            ),
            on="location"
        )
        initial_loc_prob["posterior_male"] = initial_loc_prob["prior"] * initial_loc_prob["likelihood_male"]
        initial_loc_prob["posterior_male"] /= initial_loc_prob["posterior_male"].sum()
        initial_loc_prob["posterior_female"] = initial_loc_prob["prior"] * (1-initial_loc_prob["likelihood_male"])
        initial_loc_prob["posterior_female"] /= initial_loc_prob["posterior_female"].sum()
        return initial_loc_prob
    
    def get_initial_age_prob(self):
        initial_age_prob = self.users[["sex","location","age"]].groupby(["sex","location","age"]).value_counts().reset_index()
        helper = initial_age_prob[["sex","location","count"]].groupby(["sex","location"]).sum().reset_index().copy()
        initial_age_prob["prior"] = 0.0
        initial_age_prob["likelihood"] = 0.0
        initial_age_prob["posterior"] = 0.0

        for loc in initial_age_prob["location"].unique():
            for sex in initial_age_prob.loc[initial_age_prob["location"]==loc,"sex"].unique():
                mask1 = (initial_age_prob["location"]==loc) & (initial_age_prob["sex"]==sex)
                mask2 = (helper["location"]==loc) & (helper["sex"]==sex)
                initial_age_prob.loc[mask1,"likelihood"] = initial_age_prob.loc[mask1,"count"] / helper.loc[mask2,"count"].item()
                ages = np.sort(initial_age_prob.loc[mask1,"age"].values)
                x = np.linspace(18,100,83)[ages-18]
                w = expon(loc=18,scale=20).pdf(x)
                initial_age_prob.loc[mask1,"prior"] = w / w.sum()
                initial_age_prob.loc[mask1,"posterior"] = initial_age_prob.loc[mask1,["prior","likelihood"]].prod(axis=1)
                initial_age_prob.loc[mask1,"posterior"] /= initial_age_prob.loc[mask1,"posterior"].sum()
        return initial_age_prob

    def build_model(self):

        demographics = self.users[["sex","location","age"]].groupby(["sex","location","age"]).sum().reset_index()
        cat_subcat = self.state[["category","subcategory"]].groupby(["category","subcategory"]).sum().reset_index()

        fixed_values = (
            [[str(__) for __ in cat_subcat[_].unique()] for _ in cat_subcat.columns] +
            [[str(__) for __ in demographics[_].unique()] for _ in demographics.columns[:-1]]
        )

        fixed_sizes = np.array([len(_) for _ in fixed_values])
        fixed_level_sizes = np.hstack([fixed_sizes[:2],fixed_sizes[1]* np.cumprod(fixed_sizes[2:])])
        self.__start_indices = np.hstack([0,np.cumsum(fixed_level_sizes)]) + 1

        locs = np.sort(self.users["location"].unique())

        edges = []
        self.decoder_leafs = {}
        counters = self.__start_indices.copy()
        idx_leafs = 0

        self.cat_indices = {}
        self.subcat_indices = {}

        prob_cat = self.get_prob_cat(self.state)
        for i1,cat in enumerate(np.sort(self.state["category"].unique())):
            edges.append((0,counters[0].item(),prob_cat[i1].item()))
            self.cat_indices.update({cat:(0,counters[0].item())})

            prob_sub = self.get_prob_subcat(self.state,cat) 
            for i2,subcat in enumerate(np.sort(self.state.loc[self.state["category"]==cat,"subcategory"].unique())):
                edges.append((counters[0].item(),counters[1].item(),prob_sub[i2].item()))
                self.subcat_indices.update({subcat:(counters[0].item(),counters[1].item())})
                
                prob_sex = self.get_prob_sex(cat)
                for i3,sex in enumerate(["M","F"]):
                    edges.append((counters[1].item(),counters[2].item(),prob_sex[i3].item()))
                    
                    prob_loc = self.get_prob_loc(sex)
                    for i4,loc in enumerate(locs):
                        edges.append((counters[2].item(),counters[3].item(),prob_loc[i4].item()))

                        prob_ages = self.get_prob_age(sex,loc)
                        for i5 in range(len(prob_ages)):
                            edges.append((counters[3].item(),counters[4].item(),prob_ages[i5].item()))
                            
                            self.decoder_leafs.update({idx_leafs:(i1,i2,i3,i4,i5)})
                            idx_leafs += 1
            
                            counters[4] += 1
                        counters[3] += 1
                    counters[2] += 1
                counters[1] += 1
            counters[0] += 1

        g = nx.DiGraph()
        g.add_nodes_from(range(len(edges)))
        g.add_weighted_edges_from(edges)

        self.transition_matrix = lil_matrix(nx.adjacency_matrix(g))
        self.graph = g
        
        self.decoder_data = {
            "category": np.sort(self.state["category"].unique()),
            "subcategory": {
                cat:
                np.sort(self.state.loc[self.state["category"]==cat,"subcategory"].unique())
                for cat in np.sort(self.state["category"].unique())
            },
            "sex": ["M","F"],
            "location": np.sort(self.initial_age_prob["location"].unique()),
            "age": {
                loc:{
                    sex:
                    np.sort(self.initial_age_prob.loc[(self.initial_age_prob["sex"]==sex)&(self.initial_age_prob["location"]==loc),"age"].unique())
                    for sex in ["M","F"]
                }
                for loc in np.sort(self.initial_age_prob["location"].unique())
            }
        }


    def decode(self, idx:int):
        x = self.decoder_leafs[idx]
        cat = self.decoder_data["category"][x[0]]
        sub = self.decoder_data["subcategory"][cat][x[1]]
        sex = self.decoder_data["sex"][x[2]]
        loc = self.decoder_data["location"][x[3]]
        age = self.decoder_data["age"][loc][sex][x[4]].item()
        return (cat, sub, sex, loc, age)
    

    def step(self, transition_matrix:lil_matrix, state:pd.DataFrame):
        probs = matrix_power(transition_matrix,5)[0,self.__start_indices[-1]:].toarray().ravel()
        idx = np.random.choice(np.arange(probs.size),p=probs).item()
        cat,sub,sex,loc,age = self.decode(idx)

        mask_users = (self.users["sex"]==sex) & (self.users["location"]==loc) & (self.users["age"]==age)
        user_id = self.users.loc[mask_users].sample(1)["user_id"].item()

        mask_state = (state["category"]==cat)&(state["subcategory"]==sub)&(state["available_units"]>0)
       
        vendor_id = state.loc[mask_state,"vendor_id"].iloc[[0]].item()
        product_id = state.loc[mask_state,"product_id"].iloc[[0]].item()

        state.loc[state.loc[mask_state].index[0],"available_units"] -= 1

        prob_cat = self.get_prob_cat(state)
        for i1,cat_ in enumerate(np.sort(state["category"].unique())):
            transition_matrix[*self.cat_indices[cat_]] = prob_cat[i1]

        prob_sub = self.get_prob_subcat(state, cat)
        for i2,sub_ in enumerate(np.sort(state.loc[state["category"]==cat,"subcategory"].unique())):
            transition_matrix[*self.subcat_indices[sub_]] = prob_sub[i2]
        
        return transition_matrix, state, [vendor_id, product_id, user_id]
    
    def gen_orders(self, n_orders:int):
        assert n_orders < self.metadata.n_products

        state = self.state.copy(deep=True)
        transition_matrix = self.transition_matrix.copy()

        rows = []
        for i in tqdm(range(n_orders)):
            transition_matrix, state, values = self.step(transition_matrix, state)
            rows.append([i+1,*values])

        df = pd.DataFrame(rows, columns=["order_id", "vendor_id", "product_id", "user_id"])
        return df
    
    def run(self, n_orders:int, reset_initial:bool=False, reset_state:bool=False, reset_store:bool=False):
        if reset_initial:
            self.reset_initial_prob()
        if reset_state:
            self.reset_state()
        if reset_store:
            self.reset_store()

        self.orders = self.gen_orders(n_orders)
        self.update_stock()
        return self
    
    def get_query_orders(self) -> str:
        values = ",".join(
            f"({row.order_id},{row.vendor_id},{row.product_id},{row.user_id})"
            for row in self.orders.itertuples(index=False)
        )
        return f"INSERT INTO Orders (order_id, vendor_id, product_id, user_id) VALUES {values};"

    def plot_graph(self):
        g = nx.Graph(list(self.graph.edges(data="weight")))
        fig,ax = plt.subplots(1,1,figsize=(10,10),dpi=150)
        nx.draw_kamada_kawai(g,node_size=10,with_labels=False,ax=ax)
        plt.savefig("assets/probabilistic_structure.png")
        plt.show()

    def update_stock(self):
        self.stock_updated = self.stock.copy(deep=True)
        for order in self.orders.itertuples(index=False):
            mask = (self.stock_updated["vendor_id"]==order.vendor_id)&(self.stock_updated["product_id"]==order.product_id)
            self.stock_updated.loc[mask,"available_units"] -= 1

    def get_query_stock(self, update:bool=True) -> str:
        if update:
            stock = self.stock_updated
        else:
            stock = self.stock
        values = ",".join(
            f"({row.vendor_id},{row.product_id},{row.available_units})"
            for row in stock.itertuples(index=False)
        )
        return f"INSERT INTO Stock (vendor_id, product_id, available_units) VALUES {values};"