var admin = new Vue({
    el: '#admin',
    methods: {
        get_dates: function(id){
            if(!this.kodstugor_datum[id]){
              this.$set(this.kodstugor_datum, id, []);
            }
            return this.kodstugor_datum[id]
        },
        next_date: function(list){
            if(list.slice(-1)[0]){
                var current_last_date = new Date(list.slice(-1)[0].datum);
                var new_date = new Date(current_last_date.setDate(current_last_date.getDate() + 7));
                return {'datum':new_date.toISOString().substring(0,10),'typ':'kodstuga'}
            } else {
                return {'datum':'','typ':'kodstuga'}
            }
        },
        check_send: function (theform){
            next = this
            theform.preventDefault();
            form = theform.srcElement   
            fetch(form.getAttribute("action"), {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                },
            body: $(form).serialize()
            }
            ).then(
                function(response){
                response.json(
            ).then(
                function(data){
                    Object.keys(data).forEach(function(key){
                        next[key] = data[key];
                    })
                    next.edit=""
                }
            )
            });
        },
    },
    created: function() {
        var main = this;
        fetch('/api/applied').then(
            function(response) {
                response.json().then(function(data) {
                    data.kids.forEach(function(kid) {
                        main.kids.push(kid);
                    });
                })
            });
        fetch('/api/kodstugor').then(
            function(response) {
                response.json().then(function(data) {
                    data.kodstugor.forEach(function(kodstuga) {
                        main.kodstugor.push(kodstuga);
                    });
                })
            });
        fetch('/api/datum').then(
            function(response) {
                response.json().then(function(data) {
                    main.kodstugor_datum = data.kodstugor_datum
                })
            });
        fetch('/api/kontaktpersoner').then(
            function(response) {
                response.json().then(function(data) {
                    data.kontaktpersoner.forEach(function(kontaktperson) {
                        main.kontaktpersoner.push(kontaktperson);
                    });
                })
            });
    },
    data: {
        page: "BESK",
        kids: [],
        kodstugor: [],
        kodstugor_datum: {},
        edit: "",
        kontaktpersoner: []
    }
})