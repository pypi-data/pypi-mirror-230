const ProfileApp = {
  data() {
    return {  profile_displayed: false,
              timezones_loaded: false,
              timezones: [],
              timezone: "",
              full_name: "",
              email_address : "",
              first_name : "",
              last_name : "",
              old_last_name : "",
              old_first_name : "",
              old_timezone : "",
              tzfilter: ""
            }
  },
  created() {
    /*
    axios
    .get('/arches/registration/profile/api/userinfo')
    .then(response => {
        data = response.data
        this.full_name = data["first_name"] + " " + data["last_name"]
      }
    )
    */
    this.full_name=""
  },
  methods : {
    save_profile: function() {
      config = {
          headers: { 'Content-Type': 'application/json' }
      }

      profile = {"last_name" : this.last_name, "first_name" : this.first_name, "timezone" : this.timezone}

      axios.post("/arches/registration/profile/api/userinfo", profile, config)
      .then(response => {
          this.full_name = this.first_name + " " + this.last_name
          this.old_first_name = this.first_name 
          this.old_last_name = this.last_name
          this.old_timezone = this.timezone
          this.profile_displayed = false
      })

    },
    show_profile: function() {
      if (!this.timezones_loaded) {
        axios.get("/arches/registration/profile/api/timezones")
        .then(response => {
          this.timezones = response.data


          axios
          .get('/arches/registration/profile/api/userinfo')
          .then(response => {
            data = response.data
            this.full_name = data["first_name"] + " " + data["last_name"]
            this.first_name = data["first_name"]
            this.last_name = data["last_name"]
            this.old_first_name = data["first_name"]
            this.old_last_name = data["last_name"]
            this.email_address = data["email_address"]
            this.timezone = data["timezone"]
            this.old_timezone = data["timezone"]

            this.profile_displayed = true


          }
          )


        })
      }
    },
    hide_profile: function() {
        this.profile_displayed = false
    },
    tzfilter_keypress: function(e) {
      var char_code = e.keyCode || e.which;
      if (char_code == 8 && this.tzfilter.length > 0) {
        this.tzfilter = this.tzfilter.substring(0, this.tzfilter.length-1)
      } else {
        var char_str = e.key
        if (char_str == " ") {
          char_str = "_"
        }
        if ("_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890+-\/".lastIndexOf(char_str) != -1) {
          this.tzfilter = this.tzfilter + char_str
        }
      }

      console.log(this.tzfilter)
      e.stopPropagation();
    }
  },
  computed : {
    ok_to_save: function() {
      items = [this.last_name, this.first_name, this.timezone]
      old_items = [this.old_last_name, this.old_first_name, this.old_timezone]
      items_changed = false
      no_items_blank = true
      ret_value = false

      for (i=0; i<items.length; i++) {
        if ( items[i] <= "" ) {
          no_items_blank = false
          break
        }

        if (items[i] != old_items[i]) {
          items_changed = true
        }
      }

      if (no_items_blank && items_changed) {
        ret_value = true
      }
    },
    filtered_timezones : function() {
      ret_list = this.timezones.filter(tz => {return ((this.tzfilter == "" ) || (tz.toUpperCase().indexOf(this.tzfilter.toUpperCase()) > -1)) })
      if ((ret_list.length > 0) && (!ret_list.includes(this.timezone))) {
        this.timezone = ret_list[0]
      }
      return ret_list
    }
  }
}

Vue.createApp(ProfileApp).mount('#profile')