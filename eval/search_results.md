# WeekendYatri Semantic Search Evaluation

## Evaluation Details

- Embedding Model: all-MiniLM-L6-v2
- Vector Database: ChromaDB
- Similarity Metric: Cosine Distance
- Number of Questions: 10
- Maximum Results per Question: 5
- Actual results may be fewer due to metadata filtering.

## Retrieval Results

### Q1. Find adventure destinations suitable for trekking.

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Kalsubai Mountain | Ahilyanagar | adventure | 0.5761 |
| 2 | Harishchandragad Fort | Ahilyanagar | adventure | 0.5988 |
| 3 | Anjaneri Hills | Nashik | adventure | 0.6022 |
| 4 | Ratangad Fort | Ahilyanagar | adventure | 0.6305 |
| 5 | Sandhan Valley | Ahilyanagar | adventure | 0.6311 |

**Top result document:**

```text
Destination: Kalsubai Mountain
District: Ahilyanagar
Category: adventure
Best Season: monsoon and winter
How to Reach: Reach Bari village by road; trek to the summit.
Official Details: {}
Source: https://ahilyanagar.maharashtra.gov.in/en/tourist-place-category/adventure/
```

### Q2. Suggest nature destinations in Ahilyanagar.

**Results returned: 4**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Rehkuri Blackbuck Sanctuary | Ahilyanagar | nature | 0.3638 |
| 2 | Nilwande Dam | Ahilyanagar | nature | 0.3882 |
| 3 | Mula Dam | Ahilyanagar | nature | 0.4208 |
| 4 | Bhandardara | Ahilyanagar | nature | 0.6487 |

**Top result document:**

```text
Destination: Rehkuri Blackbuck Sanctuary
District: Ahilyanagar
Category: nature
Best Season: winter
How to Reach: Reach Rehkuri village by road.
Official Details: {}
Source: https://ahilyanagar.maharashtra.gov.in/en/tourist-places/
```

### Q3. Which destinations are suitable for winter?

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Harishchandragad Fort | Ahilyanagar | adventure | 0.5640 |
| 2 | Someshwar | Nashik | religious | 0.5825 |
| 3 | Rehkuri Blackbuck Sanctuary | Ahilyanagar | nature | 0.5839 |
| 4 | Pandavleni Caves | Nashik | heritage | 0.5962 |
| 5 | Trimbakeshwar Temple | Nashik | religious | 0.6022 |

**Top result document:**

```text
Destination: Harishchandragad Fort
District: Ahilyanagar
Category: adventure
Best Season: winter
How to Reach: Reach Khireshwar or another established base village and trek.
Official Details: {}
Source: https://ahilyanagar.maharashtra.gov.in/en/tourist-places/
```

### Q4. Find heritage attractions in Chhatrapati Sambhajinagar.

**Results returned: 3**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Bibi Ka Maqbara | Chhatrapati Sambhajinagar | heritage | 0.2305 |
| 2 | Panchakki | Chhatrapati Sambhajinagar | heritage | 0.2514 |
| 3 | Daulatabad Fort | Chhatrapati Sambhajinagar | heritage | 0.3050 |

**Top result document:**

```text
Destination: Bibi Ka Maqbara
District: Chhatrapati Sambhajinagar
Category: heritage
Best Season: winter
How to Reach: Located within Sambhajinagar city; accessible by local transport.
Official Details: {}
Source: https://maharashtratourism.gov.in/districts/chhatrapati-sambhajinagar/
```

### Q5. Suggest destinations suitable for monsoon.

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Dugarwadi Falls | Nashik | nature | 0.4725 |
| 2 | Someshwar | Nashik | religious | 0.5037 |
| 3 | Mhaismal Hill Station | Chhatrapati Sambhajinagar | nature | 0.5104 |
| 4 | Kalsubai Mountain | Ahilyanagar | adventure | 0.5270 |
| 5 | Mula Dam | Ahilyanagar | nature | 0.5387 |

**Top result document:**

```text
Destination: Dugarwadi Falls
District: Nashik
Category: nature
Best Season: monsoon
How to Reach: Reach via Trimbakeshwar and continue towards the waterfall.
Official Details: {}
Source: https://nashik.gov.in/en/tourism/places-of-interest/
```

### Q6. Find religious destinations near Nashik.

**Results returned: 3**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Trimbakeshwar Temple | Nashik | religious | 0.3214 |
| 2 | Someshwar | Nashik | religious | 0.3232 |
| 3 | Kushavart Tirtha | Nashik | religious | 0.3677 |

**Top result document:**

```text
Destination: Trimbakeshwar Temple
District: Nashik
Category: religious
Best Season: winter
How to Reach: Approximately 28 km from Nashik; buses and road transport available.
Official Details: {}
Source: https://nashik.gov.in/en/tourism/tourists-places/
```

### Q7. Which destinations involve trekking to a hill or fort?

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Harishchandragad Fort | Ahilyanagar | adventure | 0.4917 |
| 2 | Ratangad Fort | Ahilyanagar | adventure | 0.5170 |
| 3 | Anjaneri Hills | Nashik | adventure | 0.5442 |
| 4 | Sandhan Valley | Ahilyanagar | adventure | 0.5886 |
| 5 | Kalsubai Mountain | Ahilyanagar | adventure | 0.6022 |

**Top result document:**

```text
Destination: Harishchandragad Fort
District: Ahilyanagar
Category: adventure
Best Season: winter
How to Reach: Reach Khireshwar or another established base village and trek.
Official Details: {}
Source: https://ahilyanagar.maharashtra.gov.in/en/tourist-places/
```

### Q8. Suggest destinations for wildlife and nature lovers.

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Dugarwadi Falls | Nashik | nature | 0.5745 |
| 2 | Rehkuri Blackbuck Sanctuary | Ahilyanagar | nature | 0.5923 |
| 3 | Mula Dam | Ahilyanagar | nature | 0.6780 |
| 4 | Salim Ali Lake | Chhatrapati Sambhajinagar | nature | 0.6860 |
| 5 | Nilwande Dam | Ahilyanagar | nature | 0.6917 |

**Top result document:**

```text
Destination: Dugarwadi Falls
District: Nashik
Category: nature
Best Season: monsoon
How to Reach: Reach via Trimbakeshwar and continue towards the waterfall.
Official Details: {}
Source: https://nashik.gov.in/en/tourism/places-of-interest/
```

### Q9. Find destinations with historical architecture.

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Gargoti Museum | Nashik | heritage | 0.5646 |
| 2 | Pandavleni Caves | Nashik | heritage | 0.6212 |
| 3 | Bibi Ka Maqbara | Chhatrapati Sambhajinagar | heritage | 0.6912 |
| 4 | Panchakki | Chhatrapati Sambhajinagar | heritage | 0.7255 |
| 5 | Daulatabad Fort | Chhatrapati Sambhajinagar | heritage | 0.7292 |

**Top result document:**

```text
Destination: Gargoti Museum
District: Nashik
Category: heritage
Best Season: all year
How to Reach: Located in Sinnar; accessible by road from Nashik.
Official Details: {}
Source: https://nashik.gov.in/en/tourism/tourists-places/
```

### Q10. Suggest weekend destinations around Nashik.

**Results returned: 5**

| Rank | Destination | District | Category | Cosine Distance |
|---:|---|---|---|---:|
| 1 | Someshwar | Nashik | religious | 0.3079 |
| 2 | Dugarwadi Falls | Nashik | nature | 0.3618 |
| 3 | Trimbakeshwar Temple | Nashik | religious | 0.3619 |
| 4 | Gargoti Museum | Nashik | heritage | 0.3636 |
| 5 | Anjaneri Hills | Nashik | adventure | 0.3838 |

**Top result document:**

```text
Destination: Someshwar
District: Nashik
Category: religious
Best Season: winter and monsoon
How to Reach: Approximately 8 km from Nashik Central Bus Stand.
Official Details: {}
Source: https://nashik.gov.in/en/tourism/places-of-interest/
```

## Evaluation Summary

- Questions evaluated: 10
- Maximum results per question: 5
- Total retrieval results: 45

## Observations

- Semantic search retrieves destinations using sentence embeddings.
- ChromaDB stores and retrieves destination vectors persistently.
- Metadata filters improve district, category and season relevance.
- Some queries may return fewer than five results when filters are applied.
- Retrieval ranking depends on the embedding model and available destination metadata.
- Cosine distance is used to compare semantic similarity; lower distance indicates greater similarity.
