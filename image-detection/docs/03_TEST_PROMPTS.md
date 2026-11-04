# 03 Test prompts: AI image generation

Plan: [02_TEST_PLAN.md](02_TEST_PLAN.md). 50 prompts: 10 subjects x 5 variants. Tool k uses variant k.

Paste the prompt, then add this sentence with the file name from the last column:

`Name the image "<file name>". Do not write any text or this name on the image.`

Tools often ignore the naming request; rename the file by hand to `<file name>.<ext>` and save it in `image-detection/test-images/own_test/fake/`.

## Variant 1: ChatGPT

| Subject | Prompt | File name |
|---|---|---|
| mountain | A photograph of a snow-capped mountain range at sunrise, seen from a valley with a small river in the foreground. | `chatgpt__mountain-1` |
| coast | A photograph of a sandy beach at low tide with gentle waves and a few footprints, late afternoon light. | `chatgpt__coast-1` |
| forest | A photograph of a narrow dirt path through a dense pine forest with sunbeams between the trees. | `chatgpt__forest-1` |
| street | A photograph of a busy city street with shops and parked cars on a rainy evening. | `chatgpt__street-1` |
| interior | A photograph of a small living room with a sofa, a bookshelf and a window with daylight. | `chatgpt__interior-1` |
| food | A photograph of a plate of pasta with tomato sauce and basil on a wooden table. | `chatgpt__food-1` |
| flower | A photograph of red tulips in a garden bed with soft morning light. | `chatgpt__flower-1` |
| animal | A photograph of a bird perched on a branch with a blurred green background. | `chatgpt__animal-1` |
| monument | A photograph of an old stone cathedral seen from the square in front of it, midday. | `chatgpt__monument-1` |
| vehicle | A photograph of a red car parked on a quiet street, taken from the side. | `chatgpt__vehicle-1` |

## Variant 2: Gemini

| Subject | Prompt | File name |
|---|---|---|
| mountain | A photo of a rocky alpine lake surrounded by steep peaks, taken on a cloudy afternoon. | `gemini__mountain-2` |
| coast | A photo of a rocky coastline with waves hitting the cliffs under an overcast sky. | `gemini__coast-2` |
| forest | A photo of a mossy stream running through an old beech forest in spring. | `gemini__forest-2` |
| street | A photo of a narrow old-town alley with stone buildings and hanging laundry, midday. | `gemini__street-2` |
| interior | A photo of a tidy kitchen with wooden cabinets and a table with two chairs. | `gemini__interior-2` |
| food | A photo of a bowl of soup with bread on the side, taken from above. | `gemini__food-2` |
| flower | A close-up photo of a bee on a yellow sunflower. | `gemini__flower-2` |
| animal | A photo of a deer standing at the edge of a meadow at dawn. | `gemini__animal-2` |
| monument | A photo of a castle on a hill above a small town, taken from across a river. | `gemini__monument-2` |
| vehicle | A photo of a passenger train arriving at a small station on a cloudy day. | `gemini__vehicle-2` |

## Variant 3: Meta AI

| Subject | Prompt | File name |
|---|---|---|
| mountain | A wide landscape photo of green hills and a dirt road leading toward distant mountains in late summer. | `metaai__mountain-3` |
| coast | A photograph of a small fishing harbour with wooden boats and a stone pier in the morning. | `metaai__coast-3` |
| forest | A photograph of tall trees covered in snow along a forest road in winter. | `metaai__forest-3` |
| street | A photograph of a suburban street lined with trees and houses on a sunny morning. | `metaai__street-3` |
| interior | A photograph of a cafe interior with a counter, stools and hanging lamps. | `metaai__interior-3` |
| food | A photograph of a fresh salad with vegetables in a white bowl, natural window light. | `metaai__food-3` |
| flower | A photograph of a meadow full of wildflowers under a blue sky. | `metaai__flower-3` |
| animal | A photograph of a cat sitting on a stone wall in the sun. | `metaai__animal-3` |
| monument | A photograph of an ancient ruined temple with columns under a clear sky. | `metaai__monument-3` |
| vehicle | A photograph of a bicycle leaning against a brick wall. | `metaai__vehicle-3` |

## Variant 4: Leonardo.ai

| Subject | Prompt | File name |
|---|---|---|
| mountain | A photograph of a mountain village with wooden houses below a steep cliff, early morning mist. | `leonardo__mountain-4` |
| coast | A photo of a quiet bay with turquoise water and a pebble beach, seen from a hillside. | `leonardo__coast-4` |
| forest | A photo of a forest clearing with ferns and fallen leaves in autumn, taken with a phone. | `leonardo__forest-4` |
| street | A photo of a market street with colourful stalls and awnings, seen from the end of the road. | `leonardo__street-4` |
| interior | A photo of a bedroom with an unmade bed and a desk next to a window. | `leonardo__interior-4` |
| food | A photo of a slice of chocolate cake on a plate next to a cup of coffee. | `leonardo__food-4` |
| flower | A photo of a pink rose with water drops after rain. | `leonardo__flower-4` |
| animal | A photo of a flock of ducks swimming on a calm pond. | `leonardo__animal-4` |
| monument | A photo of a stone bridge with arches over a river in a historic town. | `leonardo__monument-4` |
| vehicle | A photo of a fishing boat tied up at a wooden dock in the early morning. | `leonardo__vehicle-4` |

## Variant 5: Recraft

| Subject | Prompt | File name |
|---|---|---|
| mountain | A photo of a mountain ridge covered in autumn forest, taken from a hiking trail. | `recraft__mountain-5` |
| coast | A photograph of a lighthouse on a grassy headland above the sea at dusk. | `recraft__coast-5` |
| forest | A photograph of a wooden footbridge crossing a creek in a green forest. | `recraft__forest-5` |
| street | A photograph of a crosswalk and traffic lights at a city intersection at dusk. | `recraft__street-5` |
| interior | A photograph of a library reading room with long tables and tall shelves. | `recraft__interior-5` |
| food | A photograph of a breakfast table with eggs, toast and orange juice. | `recraft__food-5` |
| flower | A photograph of lavender fields in rows, taken at golden hour. | `recraft__flower-5` |
| animal | A photograph of a horse grazing in a field with hills behind it. | `recraft__animal-5` |
| monument | A photograph of a mosque with a dome and two minarets at sunset. | `recraft__monument-5` |
| vehicle | A photograph of a yellow bus on a country road with fields on both sides. | `recraft__vehicle-5` |
