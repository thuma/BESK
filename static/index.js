var admin = new Vue({
    el: '#admin',
    methods: {
        get_data: function(url){
            var main = this;
            fetch(url).then(
                function(response) {
                response.json().then(function(data) {
                    Object.keys(data).forEach(function(key){
                        main.$set(main, key, data[key])
                    })
                })
            });
        },
        copy: function(obj){
             return JSON.parse(JSON.stringify(obj));
        },
        kodstuga_name_by_id: function(id){
            var name = ""
            var kodstuga_id = id
            this.kodstugor.forEach(
                function(kodstuga){
                    if (kodstuga.id == kodstuga_id){
                        name = kodstuga.namn
                    }
                }
            )
            return name
        },
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
        get_status_for_volontar_at_date: function(id, date, plan){
            if(plan[id] == undefined){
                return ""
            } else if (plan[id][date] == undefined){
                return ""
            } else {
                return plan[id][date]["status"]
            }
        },
        get_id_for_volontar_at_date(id, date, plan){
            if(plan[id] == undefined){
                return "0"
            } else if (plan[id][date] == undefined){
                return "0"
            } else {
                return plan[id][date]["id"]
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
                if (response.status == 200){
                    response.json().then(
                        function(data){
                            Object.keys(data).forEach(function(key){
                                next[key] = data[key];
                            })
                        next.edit=""
                    })
                } else {
                    response.text().then(
                        function(data){
                            window.alert(data)
                    })
                }
            });
        },
    },
    created: function() {
        ['/api/deltagare',
        '/api/kodstugor',
        '/api/datum',
        '/api/kontaktpersoner',
        '/api/volontarer',
        '/api/volontarer_plannering',
        '/api/utskick'].forEach(this.get_data)
    },
    data: {
        page: "BESK",
        deltagare: [],
        kodstugor: [],
        kodstugor_datum: {},
        edit: "",
        kontaktpersoner: [],
        volontärer: [],
        volontarer_plannering: {},
        utskick: []
    }
})