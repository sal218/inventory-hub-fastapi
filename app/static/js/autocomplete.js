
function autocomplete(categories) {
    return {
        query: '',
        selected: null,
        categories: categories,
        get filtered() {
            if (!this.query) {
                return this.categories;
            }
            return this.categories.filter(item => 
                item.name.toLowerCase().includes(this.query.toLowerCase())
            );
        },
        select(item) {
            this.query = item.name;
            this.selected = item;
        }
    }
}

