const mapCopilot = obj => {
  obj._data = _.clone(obj)

  obj.theTime = obj.time * 60 - (Date.now() / 1000 - obj.timestamp)
  obj.time = obj.time + 'mins'

  if (obj.time_elapsed) {
    obj.date = 'Time elapsed'
  } else {
    obj.date = Quasar.date.formatDate(
      new Date((obj.theTime - 3600) * 1000),
      'HH:mm:ss'
    )
  }
  obj.displayComposeUrl = ['/copilot/cp/', obj.id].join('')
  obj.displayPanelUrl = ['/copilot/', obj.id].join('')
  return obj
}

window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      filter: '',
      copilotLinks: [],
      copilotLinksObj: [],
      copilotsTable: {
        columns: [
          {
            name: 'theId',
            align: 'left',
            label: 'id',
            field: 'id'
          },
          {
            name: 'lnurl_toggle',
            align: 'left',
            label: 'Show lnurl pay link',
            field: 'lnurl_toggle'
          },
          {
            name: 'title',
            align: 'left',
            label: 'title',
            field: 'title'
          },
          {
            name: 'amount_made',
            align: 'left',
            label: 'amount made',
            field: 'amount_made'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      passedCopilot: {},
      formDialog: {
        show: false,
        data: {}
      },
      formDialogCopilot: {
        show: false,
        data: {
          lnurl_toggle: false,
          show_message: false,
          show_ack: false,
          show_price: 'None',
          title: ''
        }
      },
      qrCodeDialog: {
        show: false,
        data: null
      },
      options: ['bitcoin', 'confetti', 'rocket', 'face', 'martijn', 'rick'],
      currencyOptions: ['None', 'btcusd', 'btceur', 'btcgbp']
    }
  },
  methods: {
    cancelCopilot(data) {
      this.formDialogCopilot.show = false
      this.clearFormDialogCopilot()
    },
    closeFormDialog() {
      this.clearFormDialogCopilot()
      this.formDialog.data = {
        lnurl_toggle: false,
        show_message: false,
        show_ack: false,
        show_price: 'None',
        title: ''
      }
    },
    sendFormDataCopilot() {
      if (this.formDialogCopilot.data.id) {
        this.updateCopilot(
          this.g.user.wallets[0].adminkey,
          this.formDialogCopilot.data
        )
      } else {
        this.createCopilot(
          this.g.user.wallets[0].adminkey,
          this.formDialogCopilot.data
        )
      }
    },

    createCopilot(wallet, data) {
      const updatedData = {}
      for (const property in data) {
        if (data[property]) {
          updatedData[property] = data[property]
        }
        if (property == 'animation1threshold' && data[property]) {
          updatedData[property] = parseInt(data[property])
        }
        if (property == 'animation2threshold' && data[property]) {
          updatedData[property] = parseInt(data[property])
        }
        if (property == 'animation3threshold' && data[property]) {
          updatedData[property] = parseInt(data[property])
        }
      }

      LNbits.api
        .request('POST', '/copilot/api/v1/copilot', wallet, updatedData)
        .then(response => {
          this.copilotLinks.push(mapCopilot(response.data))
          this.formDialogCopilot.show = false
          this.clearFormDialogCopilot()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getCopilots() {
      LNbits.api
        .request('GET', '/copilot/api/v1/copilot', this.g.user.wallets[0].inkey)
        .then(response => {
          if (response.data) {
            this.copilotLinks = response.data.map(mapCopilot)
          }
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getCopilot(copilot_id) {
      LNbits.api
        .request(
          'GET',
          '/copilot/api/v1/copilot/' + copilot_id,
          this.g.user.wallets[0].inkey
        )
        .then(response => {
          localStorage.setItem('copilot', JSON.stringify(response.data))
          localStorage.setItem('inkey', this.g.user.wallets[0].inkey)
        })
        .catch(LNbits.utils.notifyApiError)
    },
    openCopilotCompose(copilot_id) {
      this.getCopilot(copilot_id)
      let params =
        'scrollbars=no, resizable=no,status=no,location=no,toolbar=no,menubar=no,width=1200,height=644,left=410,top=100'
      open('../copilot/cp/', '_blank', params)
    },
    openCopilotPanel(copilot_id) {
      this.getCopilot(copilot_id)
      let params =
        'scrollbars=no, resizable=no,status=no,location=no,toolbar=no,menubar=no,width=300,height=450,left=10,top=400'
      open('../copilot/pn/', '_blank', params)
    },
    deleteCopilotLink(copilotId) {
      const link = _.findWhere(this.copilotLinks, {id: copilotId})
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this pay link?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/copilot/api/v1/copilot/' + copilotId,
              this.g.user.wallets[0].adminkey
            )
            .then(response => {
              this.copilotLinks = _.reject(this.copilotLinks, function (obj) {
                return obj.id === copilotId
              })
            })
            .catch(LNbits.utils.notifyApiError)
        })
    },
    openUpdateCopilotLink(copilotId) {
      const copilot = _.findWhere(this.copilotLinks, {id: copilotId})
      this.formDialogCopilot.data = {...copilot._data}
      this.formDialogCopilot.data.lnurl_toggle = Boolean(
        this.formDialogCopilot.data.lnurl_toggle
      )
      this.formDialogCopilot.data.show_message = Boolean(
        this.formDialogCopilot.data.show_message
      )
      this.formDialogCopilot.data.show_ack = Boolean(
        this.formDialogCopilot.data.show_ack
      )
      this.formDialogCopilot.show = true
    },
    updateCopilot(wallet, data) {
      const updatedData = {}

      const updateThreshold = property => {
        if (data[property] && data[property] !== 0) {
          updatedData[property] = parseInt(data[property])
        }
      }

      for (const property in data) {
        if (data[property]) {
          updatedData[property] = data[property]
        }
        switch (property) {
          case 'animation1threshold':
          case 'animation2threshold':
          case 'animation3threshold':
            updateThreshold(property)
            break
        }
      }

      LNbits.api
        .request(
          'PUT',
          '/copilot/api/v1/copilot/' + updatedData.id,
          wallet,
          updatedData
        )
        .then(response => {
          this.copilotLinks = _.reject(this.copilotLinks, function (obj) {
            return obj.id === updatedData.id
          })
          this.copilotLinks.push(mapCopilot(response.data))
          this.formDialogCopilot.show = false
          this.clearFormDialogCopilot()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    clearFormDialogCopilot() {
      this.formDialogCopilot.data = {
        lnurl_toggle: false,
        show_message: false,
        show_ack: false,
        show_price: 'None',
        title: ''
      }
    },
    exportcopilotCSV() {
      LNbits.utils.exportCSV(this.copilotsTable.columns, this.copilotLinks)
    }
  },
  created() {
    this.getCopilots()
  }
})
