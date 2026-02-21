module.exports = {
  apps: [{
    name: 'upbit-bot',
    script: 'upbit-smart-bot-v8.0-ULTIMATE.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production'
    },
    error_file: '/tmp/upbit-bot-error.log',
    out_file: '/tmp/upbit-bot-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
}
