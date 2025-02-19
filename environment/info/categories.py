max_depth = 2

categories = [
    {'class_name': 'character', 'category 1': 'Characters'},
    {'class_name': 'bathroom', 'category 1': 'Rooms'},
    {'class_name': 'wall', 'category 1': 'Structural Elements'},
    {'class_name': 'ceiling', 'category 1': 'Structural Elements'},
    {'class_name': 'floor', 'category 1': 'Structural Elements'},
    {'class_name': 'toilet', 'category 1': 'Fixtures', 'category 2': 'Bathroom'},
    {'class_name': 'stall', 'category 1': 'Fixtures', 'category 2': 'Bathroom'},
    {'class_name': 'bathroomcabinet', 'category 1': 'Furniture', 'category 2': 'Bathroom'},
    {'class_name': 'waterglass', 'category 1': 'Kitchenware'},
    {'class_name': 'barsoap', 'category 1': 'Accessories', 'category 2': 'Bathroom'},
    {'class_name': 'deodorant', 'category 1': 'Personal Care Items'},
    {'class_name': 'bathroomcounter', 'category 1': 'Furniture', 'category 2': 'Bathroom'},
    {'class_name': 'sink', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'faucet', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'curtains', 'category 1': 'Home Decor', 'category 2': 'Textiles'},
    {'class_name': 'toothbrush', 'category 1': 'Personal Care Items'},
    {'class_name': 'facecream', 'category 1': 'Personal Care Items'},
    {'class_name': 'hairproduct', 'category 1': 'Personal Care Items'},
    {'class_name': 'toothpaste', 'category 1': 'Personal Care Items'},
    {'class_name': 'toiletpaper', 'category 1': 'Supplies', 'category 2': 'Bathroom'},
    {'class_name': 'rug', 'category 1': 'Home Decor', 'category 2': 'Textiles'},
    {'class_name': 'wallpictureframe', 'category 1': 'Home Decor', 'category 2': 'Artwork'},
    {'class_name': 'walllamp', 'category 1': 'Lighting', 'category 2': 'Wall Mounted'},
    {'class_name': 'ceilinglamp', 'category 1': 'Lighting', 'category 2': 'Ceiling Mounted'},
    {'class_name': 'doorjamb', 'category 1': 'Doors', 'category 2': 'Components'},
    {'class_name': 'door', 'category 1': 'Doors'},
    {'class_name': 'lightswitch', 'category 1': 'Electronics'},
    {'class_name': 'washingmachine', 'category 1': 'Appliances', 'category 2': 'Laundry'},
    {'class_name': 'bedroom', 'category 1': 'Rooms'},
    {'class_name': 'window', 'category 1': 'Structural Elements'},
    {'class_name': 'nightstand', 'category 1': 'Furniture', 'category 2': 'Bedroom'},
    {'class_name': 'desk', 'category 1': 'Furniture', 'category 2': 'Office'},
    {'class_name': 'chair', 'category 1': 'Furniture', 'category 2': 'Seating'},
    {'class_name': 'bookshelf', 'category 1': 'Furniture', 'category 2': 'Storage'},
    {'class_name': 'bed', 'category 1': 'Furniture', 'category 2': 'Bedroom'},
    {'class_name': 'sofa', 'category 1': 'Furniture', 'category 2': 'Living Room'},
    {'class_name': 'coffeetable', 'category 1': 'Furniture', 'category 2': 'Living Room'},
    {'class_name': 'cabinet', 'category 1': 'Furniture', 'category 2': 'Storage'},
    {'class_name': 'computer', 'category 1': 'Electronics', 'category 2': 'Computing'},
    {'class_name': 'cpuscreen', 'category 1': 'Electronics', 'category 2': 'Computing'},
    {'class_name': 'keyboard', 'category 1': 'Electronics', 'category 2': 'Computing'},
    {'class_name': 'mouse', 'category 1': 'Electronics', 'category 2': 'Computing'},
    {'class_name': 'mousemat', 'category 1': 'Electronics', 'category 2': 'Computing'},
    {'class_name': 'radio', 'category 1': 'Electronics', 'category 2': 'Audio Equipment'},
    {'class_name': 'mug', 'category 1': 'Kitchenware'},
    {'class_name': 'book', 'category 1': 'Reading Material'},
    {'class_name': 'photoframe', 'category 1': 'Home Decor'},
    {'class_name': 'box', 'category 1': 'Storage'},
    {'class_name': 'paper', 'category 1': 'Office Supplies'},
    {'class_name': 'papertray', 'category 1': 'Office Supplies', 'category 2': 'Organization'},
    {'class_name': 'cellphone', 'category 1': 'Electronics', 'category 2': 'Communication Devices'},
    {'class_name': 'folder', 'category 1': 'Office Supplies', 'category 2': 'Organization'},
    {'class_name': 'apple', 'category 1': 'Food', 'category 2': 'Fruits'},
    {'class_name': 'bananas', 'category 1': 'Food', 'category 2': 'Fruits'},
    {'class_name': 'lime', 'category 1': 'Food', 'category 2': 'Fruits'},
    {'class_name': 'peach', 'category 1': 'Food', 'category 2': 'Fruits'},
    {'class_name': 'plum', 'category 1': 'Food', 'category 2': 'Fruits'},
    {'class_name': 'dishbowl', 'category 1': 'Kitchenware', 'category 2': 'Dishes'},
    {'class_name': 'pillow', 'category 1': 'Home Decor', 'category 2': 'Textiles'},
    {'class_name': 'tablelamp', 'category 1': 'Lighting', 'category 2': 'Tabletop'},
    {'class_name': 'kitchen', 'category 1': 'Rooms'},
    {'class_name': 'cutleryknife', 'category 1': 'Kitchenware', 'category 2': 'Utensils'},
    {'class_name': 'knifeblock', 'category 1': 'Kitchenware', 'category 2': 'Storage'},
    {'class_name': 'fryingpan', 'category 1': 'Kitchenware', 'category 2': 'Cookware'},
    {'class_name': 'cookingpot', 'category 1': 'Kitchenware', 'category 2': 'Cookware'},
    {'class_name': 'plate', 'category 1': 'Kitchenware', 'category 2': 'Dishes'},
    {'class_name': 'dishwashingliquid', 'category 1': 'Cleaning Supplies'},
    {'class_name': 'condimentshaker', 'category 1': 'Kitchenware', 'category 2': 'Utensils'},
    {'class_name': 'clothespile', 'category 1': 'Clothing', 'category 2': 'Unsorted'},
    {'class_name': 'garbagecan', 'category 1': 'Containers', 'category 2': 'Waste Disposal'},
    {'class_name': 'candle', 'category 1': 'Home Decor', 'category 2': 'Lighting'},
    {'class_name': 'bench', 'category 1': 'Furniture', 'category 2': 'Seating'},
    {'class_name': 'kitchentable', 'category 1': 'Furniture', 'category 2': 'Kitchen'},
    {'class_name': 'tvstand', 'category 1': 'Furniture', 'category 2': 'Living Room'},
    {'class_name': 'kitchencabinet', 'category 1': 'Furniture', 'category 2': 'Kitchen'},
    {'class_name': 'kitchencounter', 'category 1': 'Furniture', 'category 2': 'Kitchen'},
    {'class_name': 'kitchencounterdrawer', 'category 1': 'Furniture', 'category 2': 'Kitchen'},
    {'class_name': 'stovefan', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'fridge', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'stove', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'oventray', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'dishwasher', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'coffeemaker', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'coffeepot', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'toaster', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'breadslice', 'category 1': 'Food'},
    {'class_name': 'microwave', 'category 1': 'Appliances', 'category 2': 'Kitchen'},
    {'class_name': 'chicken', 'category 1': 'Food', 'category 2': 'Meat'},
    {'class_name': 'cutlets', 'category 1': 'Food', 'category 2': 'Meat'},
    {'class_name': 'creamybuns', 'category 1': 'Food', 'category 2': 'Bakery'},
    {'class_name': 'chips', 'category 1': 'Food', 'category 2': 'Snacks'},
    {'class_name': 'chocolatesyrup', 'category 1': 'Food', 'category 2': 'Condiments'},
    {'class_name': 'poundcake', 'category 1': 'Food', 'category 2': 'Bakery'},
    {'class_name': 'livingroom', 'category 1': 'Rooms'},
    {'class_name': 'closet', 'category 1': 'Furniture', 'category 2': 'Storage'},
    {'class_name': 'tv', 'category 1': 'Electronics', 'category 2': 'Entertainment'},
    {'class_name': 'powersocket', 'category 1': 'Electronics'},
    {'class_name': 'orchid', 'category 1': 'Home Decor', 'category 2': 'Plants'},
    {'class_name': 'hanger', 'category 1': 'Home Accessories', 'category 2': 'Storage'},
    {'class_name': 'clothesshirt', 'category 1': 'Clothing'},
    {'class_name': 'clothespants', 'category 1': 'Clothing'},
    {'class_name': 'remotecontrol', 'category 1': 'Electronics', 'category 2': 'Home Automation'},
    {'class_name': 'beer', 'category 1': 'Beverages', 'category 2': 'Alcoholic Drinks'},
    {'class_name': 'wallphone', 'category 1': 'Electronics', 'category 2': 'Communication Devices'},
    {'class_name': 'bathtub', 'category 1': 'Fixtures', 'category 2': 'Bathroom'},
    {'class_name': 'towelrack', 'category 1': 'Furniture', 'category 2': 'Bathroom'},
    {'class_name': 'wallshelf', 'category 1': 'Furniture', 'category 2': 'Storage'},
    {'class_name': 'towel', 'category 1': 'Home Decor', 'category 2': 'Textiles'},
    {'class_name': 'perfume', 'category 1': 'Personal Care Items', 'category 2': 'Fragrances'},
    {'class_name': 'painkillers', 'category 1': 'Healthcare', 'category 2': 'Medicine'},
    {'class_name': 'closetdrawer', 'category 1': 'Furniture', 'category 2': 'Storage'},
    {'class_name': 'cupcake', 'category 1': 'Food', 'category 2': 'Bakery'},
    {'class_name': 'wineglass', 'category 1': 'Kitchenware'},
    {'class_name': 'slippers', 'category 1': 'Clothing', 'category 2': 'Footwear'},
    {'class_name': 'clock', 'category 1': 'Electronics', 'category 2': 'Timekeeping'},
    {'class_name': 'washingsponge', 'category 1': 'Cleaning Supplies'},
    {'class_name': 'cutleryfork', 'category 1': 'Kitchenware', 'category 2': 'Utensils'},
    {'class_name': 'condimentbottle', 'category 1': 'Kitchenware', 'category 2': 'Containers'},
    {'class_name': 'whippedcream', 'category 1': 'Food', 'category 2': 'Dairy Products'},
    {'class_name': 'pie', 'category 1': 'Food', 'category 2': 'Bakery'},
    {'class_name': 'bellpepper', 'category 1': 'Food', 'category 2': 'Vegetables'},
    {'class_name': 'salmon', 'category 1': 'Food', 'category 2': 'Seafood'},
    {'class_name': 'candybar', 'category 1': 'Food', 'category 2': 'Snacks'},
    {'class_name': 'crackers', 'category 1': 'Food', 'category 2': 'Snacks'},
    {'class_name': 'cereal', 'category 1': 'Food', 'category 2': 'Breakfast Items'},
    {'class_name': 'juice', 'category 1': 'Beverages', 'category 2': 'Non-Alcoholic Drinks'},
    {'class_name': 'milk', 'category 1': 'Beverages', 'category 2': 'Dairy'},
    {'class_name': 'mincedmeat', 'category 1': 'Food', 'category 2': 'Meat'},
    {'class_name': 'toy', 'category 1': 'Home Accessories', 'category 2': 'Recreational Items'},
    {'class_name': 'printer', 'category 1': 'Electronics', 'category 2': 'Office'},
    {'class_name': 'cuttingboard', 'category 1': 'Kitchenware', 'category 2': 'Utensils'},
    {'class_name': 'carrot', 'category 1': 'Food', 'category 2': 'Vegetables'},
    {'class_name': 'salad', 'category 1': 'Food', 'category 2': 'Vegetables'},
    {'class_name': 'magazine', 'category 1': 'Reading Material', 'category 2': 'Entertainment'},
    {'class_name': 'notes', 'category 1': 'Office Supplies'}
]


if __name__ == "__main__":
    # Removing duplicate entries based on 'class_name'
    unique_categories = {each['class_name']: each for each in categories}.values()

    # Converting the result back to a list
    unique_categories_list = list(unique_categories)

    # Formatting the complete list for printing
    formatted_complete_list = "categories = [\n" + ",\n".join("    " + str(item) for item in unique_categories_list) + "\n]"

    # Since the string is too long to display in the output window, we'll write it to a text file
    with open('unique_categories_formatted.txt', 'w') as file:
        file.write(formatted_complete_list)