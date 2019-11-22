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
        get_data_volontar_at_date: function(id, date){
            if(this.volontarer_plannering[id] == undefined){
                return {"status":"", "id":0, "kommentar":""}
            } else if (this.volontarer_plannering[id][date] == undefined){
                return {"status":"", "id":0, "kommentar":""}
            } else {
                return this.volontarer_plannering[id][date]
            }
        },
        get_data_for_deltagare_at_date: function(id, date){
            if(this.närvaro[id] == undefined){
                return {"status":"","id":0}
            } else if (this.närvaro[id][date] == undefined){
                return {"status":"","id":0}
            } else {
                return this.närvaro[id][date]
            }
        },
        är_ja: function(data, id, date){
            return this.get_data_volontar_at_date(id, date)['status'].toUpperCase().includes("JA")
        },
        är_nej: function(data, id, date){
            return this.get_data_volontar_at_date(id, date)['status'].toUpperCase().includes("NEJ")
        },
        button_color_volontär: function(data, id, date){
            if (this.är_nej(data, id, date)){
                return {'btn-outline-danger':true}
            } else if (this.är_ja(data, id, date)){
                return {'btn-outline-success':true}
            } else {
                return {'btn-outline-warning':true}
            }
        },
        button_color_närvaro: function(id, date){
            if (this.get_data_for_deltagare_at_date(id, date)['status'].toUpperCase().includes("NEJ")){
                return {'btn-outline-danger':true}
            } else if (this.get_data_for_deltagare_at_date(id, date)['status'].toUpperCase().includes("JA")){
                return {'btn-outline-success':true}
            } else {
                return {'btn-outline-warning':true}
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
        '/api/utskick',
        '/api/narvaro',
        '/api/texter'].forEach(this.get_data)
    },
    data: {
        markdown_to_html: new showdown.Converter(),
        page: "BESK",
        deltagare: [],
        närvaro:{},
        närvaro_redigerade: {},
        kodstugor: [],
        kodstugor_datum: {},
        edit: "",
        kontaktpersoner: [],
        volontärer: [],
        volontarer_plannering: {},
        volontarer_redigerade: {},
        utskick: [],
        texter: [],
    }
})