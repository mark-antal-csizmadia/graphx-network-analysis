class LabelPropagationPredictor():
    def __init__(self, g, max_iter):
        self.max_iter = max_iter
        self.communities = g.labelPropagation(maxIter=self.max_iter)
        print("LabelPropagationPredictor has been fit to graph")

    def get_communities(self, ):
        return communities.persist()

    def __call__(self, id_):
        id_label = self.communities.filter(f"id == {id_}").select("label").collect()[0]["label"]
        recommendations = communities.filter(f"label == {id_label}")
        return recommendations


class JaccardSimilarityPredictor():
    def __init__(self):
        pass

    def get_neighbour_ids(self, g, id_):
        triplets = g.triplets.filter(f"src.id == {id_}")
        return set([row["dst"]["id"] for row in triplets.collect()])

    def jaccard_sim(self, a, b):
        return len(a.intersection(b)) / len(a.union(b))

    def __call__(self, g, id_):
        # get neighbours of node
        ids_neighbour = get_neighbour_ids(g, id_)

        similarities = []

        for id_neighbour in ids_neighbour:
            # get neighbours of neighbour node
            ids_neighbours_of_neighbour = get_neighbour_ids(g, id_neighbour)
            js = jaccard_sim(ids_neighbour, ids_neighbours_of_neighbour)
            similarities.append((id_neighbour, js))

        similarities_df = spark.createDataFrame(similarities, ["id", "jaccard"])

        return g.vertices. \
            join(similarities_df, g.vertices["id"] == similarities_df["id"], "inner"). \
            drop(similarities_df.id). \
            sort(desc("jaccard"))