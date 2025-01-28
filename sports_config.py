SUPPORTED_SPORTS = {
    'soccer': {'id': 1, 'name': 'Soccer'},
    'basketball': {'id': 18, 'name': 'Basketball'},
    'tennis': {'id': 13, 'name': 'Tennis'},
    'volleyball': {'id': 91, 'name': 'Volleyball'},
    'handball': {'id': 78, 'name': 'Handball'},
    'baseball': {'id': 16, 'name': 'Baseball'},
    'ice_hockey': {'id': 17, 'name': 'Ice Hockey'},
    'american_football': {'id': 12, 'name': 'American Football'},
    'snooker': {'id': 14, 'name': 'Snooker'},
    'darts': {'id': 15, 'name': 'Darts'},
    'table_tennis': {'id': 92, 'name': 'Table Tennis'},
    'badminton': {'id': 94, 'name': 'Badminton'},
    'rugby_league': {'id': 19, 'name': 'Rugby League'},
    'australian_rules': {'id': 36, 'name': 'Australian Rules'},
    'beach_volleyball': {'id': 95, 'name': 'Beach Volleyball'}
}

# API Endpoints
API_ENDPOINTS = {
    'fixtures': '/fixtures',
    'live': '/fixtures/live',
    'leagues': '/leagues',
    'teams': '/teams',
    'standings': '/standings',
    'players': '/players',
    'statistics': '/statistics',
    'odds': '/odds'
}

# Sport-specific scoring formats
SPORT_SCORING = {
    'soccer': {'main_stat': 'goals', 'format': '{home_score} - {away_score}'},
    'basketball': {'main_stat': 'points', 'format': '{home_score} - {away_score}'},
    'tennis': {'main_stat': 'sets', 'format': 'Sets: {sets}, Games: {games}'},
    'volleyball': {'main_stat': 'sets', 'format': 'Sets: {sets}'},
    'handball': {'main_stat': 'goals', 'format': '{home_score} - {away_score}'},
    'baseball': {'main_stat': 'runs', 'format': '{home_score} - {away_score}'},
    'ice_hockey': {'main_stat': 'goals', 'format': '{home_score} - {away_score}'},
    'american_football': {'main_stat': 'points', 'format': '{home_score} - {away_score}'},
    'snooker': {'main_stat': 'frames', 'format': 'Frames: {frames}'},
    'darts': {'main_stat': 'sets', 'format': 'Sets: {sets}, Legs: {legs}'},
    'table_tennis': {'main_stat': 'sets', 'format': 'Sets: {sets}'},
    'badminton': {'main_stat': 'sets', 'format': 'Sets: {sets}'},
    'rugby_league': {'main_stat': 'points', 'format': '{home_score} - {away_score}'},
    'australian_rules': {'main_stat': 'points', 'format': '{home_score} - {away_score}'},
    'beach_volleyball': {'main_stat': 'sets', 'format': 'Sets: {sets}'}
}

# Event types to monitor
EVENT_TYPES = {
    'soccer': ['Goal', 'Card', 'Substitution', 'Penalty'],
    'basketball': ['2-Point', '3-Point', 'Free Throw', 'Foul'],
    'tennis': ['Point', 'Game', 'Set', 'Match'],
    'volleyball': ['Point', 'Set', 'Timeout'],
    'handball': ['Goal', 'Penalty', 'Timeout'],
    'baseball': ['Run', 'Hit', 'Error', 'Inning'],
    'ice_hockey': ['Goal', 'Penalty', 'Power Play'],
    'american_football': ['Touchdown', 'Field Goal', 'Safety', 'Conversion'],
    'snooker': ['Frame', 'Break', 'Foul'],
    'darts': ['Set', 'Leg', '180'],
    'table_tennis': ['Point', 'Set', 'Match'],
    'badminton': ['Point', 'Set', 'Match'],
    'rugby_league': ['Try', 'Conversion', 'Penalty'],
    'australian_rules': ['Goal', 'Behind', 'Mark'],
    'beach_volleyball': ['Point', 'Set', 'Match']
}
