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
        radera_text: function(id){
            this.delete_data('/api/texter',"id="+encodeURIComponent(id))
        },
        radera_utskick: function(id){
            this.delete_data('/api/utskick',"id="+encodeURIComponent(id))
        },
        radera_kodstuga: function(id){
            this.delete_data('/api/kodstugor',"id="+encodeURIComponent(id))
        },
        radera_deltagare: function(id){
            this.delete_data('/api/deltagare',"id="+encodeURIComponent(id))
        },
        radera_volontär: function(id){
            this.delete_data('/api/volontarer',"id="+encodeURIComponent(id))
        },
        delete_data: function(url, body){
            var next = this
            fetch(url, {
                method: 'DELETE',
                credentials: 'same-origin',
                headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: body
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
                            swal({text: data, icon:"error"});
                    })
                }
            });
        },
        copy: function(obj){
             return JSON.parse(JSON.stringify(obj));
        },
        volontär_finns: function(epost){
            var status = false
            var epost_in = epost
            this.volontärer.forEach(function(vol){
                if(vol.epost == epost_in){
                    status = true
                }
            })
            return status
        },
        kontaktperson_by_id: function(id){
            var data
            var kontaktpersoner_id = id
            this.kontaktpersoner.forEach(
                function(kontaktperson){
                    if (kontaktperson.id == kontaktpersoner_id){
                        data = kontaktperson
                    }
                }
            )
            return data
        },
        deltagare_by_id: function(id){
            var data
            var deltagare_id = id
            this.deltagare.forEach(
                function(kid){
                    if (kid.deltagare_id == deltagare_id){
                        data = kid
                    }
                }
            )
            return data
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
            return this.kodstugor_datum.filter(one_date => one_date.kodstugor_id == id)
        },
        next_date: function(list){
            if(list.slice(-1)[0]){
                var current_last_date = new Date(list.slice(-1)[0].datum);
                var new_date = new Date(current_last_date.setDate(current_last_date.getDate() + 7));
                return {'datum':new_date.toISOString().substring(0,10), 'typ':'kodstuga'}
            } else {
                return {'datum':'','typ':'kodstuga'}
            }
        }, 
        get_data_volontar_at_date: function(id, date){
            found_vol_data = this.volontarer_plannering.find(
                vol_data => 
                    vol_data.volontarer_id == id &&
                    vol_data.datum == date);
            if (found_vol_data) {
                return found_vol_data
            } 
            return {"status":"Ja", "id":0, "kommentar":""}
        },
        get_data_for_deltagare_at_date: function(id, date){
            found_deltagare_data = this.närvaro.find(
                delt_data => 
                    delt_data.deltagare_id == id &&
                    delt_data.datum == date);
            if (found_deltagare_data) {
                return found_deltagare_data
            } 
            return {"status":"","id":0}
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
        show_skonto: function(skonto, slosen){
            var div_data  = document.createElement("div");
            div_data.innerHTML = "<strong>Konto:</strong> " + skonto + "<br>" +
                "<strong>Lösenord:</strong> " + slosen;
            swal({
                content: div_data,
            });
        },
        show_kontaktperson: function(kontaktperson){
            var div_data  = document.createElement("div");
            div_data.innerHTML = "<strong>Namn:</strong> " + kontaktperson.fornamn + " " + kontaktperson.fornamn + "<br>" +
                "<strong>E-Post:</strong> " + kontaktperson.epost + "<br>" +
                "<strong>Telefon:</strong> " + kontaktperson.telefon;
            swal({
                content: div_data,
            });
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
                            swal({text: data, icon:"error"});
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
        '/api/texter',
        '/api/volontarer/slack',
        '/api/admin',
        '/api/me',
        '/api/loggar'].forEach(this.get_data)
    },
    computed: {
        vald_kodstuga: function(){
            var kodstuga_data = "";
            var id = this.val_kodstuga
            this.kodstugor.forEach(function(kodstuga){
                if (kodstuga.id == id){
                    kodstuga_data = kodstuga;
                }
            });
            return kodstuga_data 
        },
        statistik: function(){
            var kodstug_stats = []
            var next = this;
            this.kodstugor.forEach(function(kodstuga){
                var data = {}
                data.id = kodstuga.id
                var deltagare_alla = next.deltagare.filter(
                    deltagare => deltagare.kodstuga_id == kodstuga.id
                    );
                var närvaro_deltagare_f = deltagare_alla.filter(
                    deltagare => deltagare.kon == "hon"
                    );
                var närvaro_deltagare_p = deltagare_alla.filter(
                    deltagare => deltagare.kon == "han"
                    );
                var deltagare_ja = deltagare_alla.filter(
                    deltagare => deltagare.status == "ja"
                    );
                data.deltagare = deltagare_ja.length;
                data.flickor = deltagare_ja.filter(
                    deltagare => deltagare.kon == "hon"
                    ).length;
                data.pojkar = deltagare_ja.filter(
                    deltagare => deltagare.kon == "han"
                    ).length;
                data.volontärer = next.volontärer.filter(
                    volontär => volontär.kodstugor_id == kodstuga.id
                    ).length;
                närvaro_lista = next.närvaro.filter(
                    svar => svar.status == "ja"
                    &&
                    deltagare_alla.find(
                        deltagare => deltagare.deltagare_id == svar.deltagare_id
                        )
                    );
                data.närvaro = närvaro_lista.length;
                data.närvaro_flickor = närvaro_lista.filter(
                    närvaro => närvaro_deltagare_f.find(
                        deltagare => deltagare.deltagare_id == närvaro.deltagare_id
                        )
                    ).length;
                data.närvaro_pojkar = närvaro_lista.filter(
                    närvaro => närvaro_deltagare_p.find(
                        deltagare => deltagare.deltagare_id == närvaro.deltagare_id
                        )
                    ).length;
                data.antal_tillfällen = next.get_dates(kodstuga.id).length
                kodstug_stats.push(data)
            });
            return kodstug_stats 
        },
        statistik_tot: function(){
            return this.statistik.reduce(function(total, one){
                var ntotal = total;
                var nione = one;
                Object.keys(one).forEach(function(key){
                    if (ntotal[key]) {
                        ntotal[key] += nione[key];
                    } else {
                        ntotal[key] = nione[key];
                    }
                    
                });
                return ntotal;
            },{})
        }
    },
    data: {
        markdown_to_html: new showdown.Converter(),
        page: "BESK",
        deltagare: [],
        närvaro: [],
        närvaro_redigerade: {},
        kodstugor: [],
        kodstugor_datum: [],
        edit: "",
        kontaktpersoner: [],
        volontärer: [],
        volontarer_plannering: [],
        volontarer_redigerade: {},
        volontärer_slack: [],
        utskick: [],
        texter: [],
        me: {},
        admins: [],
        loggar: [],
        logdata: [],
        val_kodstuga: "alla"
    }
})