var app = angular.module('nvdbkontoutskrift', ['ngSanitize']);


app.run(['$rootScope', 'nvdb', function($rootScope, nvdb) {

    /*  Applikasjonen initialiseres

        Datasett:
        En liste over objekttyper og tilhørende egenskapstyper som skal være i tabellen.
        Er delt inn i kategorier

        Resultatsett:
        Resultat på en gitt dato

        1. Henter liste over datasett
        2. Henter liste over områder
        3. Henter liste over lagrede resultatsett
        4. Henter det siste resultsettet, og aktiverer det
    */

    // Henter siste lagrede resultatsett
    $rootScope.resultatsett = {};   // Lager for alle resultatsett
    $rootScope.resultat = {};       // Aktive resultater

    // Henter liste over tilgjengelige resultatsett
    nvdb.historikk().then(function(promise) {

        $rootScope.historikk = promise.data;
        $rootScope.dato = $rootScope.historikk[0];

        // Henter
        nvdb.dato($rootScope.historikk[0]).then(function(promise) {
            $rootScope.resultatsett[$rootScope.dato] = promise.data;
            $rootScope.resultat = $rootScope.resultatsett[$rootScope.dato];
        });
    });


    // Henter liste over datasett
    $rootScope.datasett = {};
    nvdb.datasett(1).then(function(promise) {
        $rootScope.datasett[1] = promise.data;
    });
    nvdb.datasett(2).then(function(promise) {
        $rootScope.datasett[2] = promise.data;
    });
    nvdb.datasett(3).then(function(promise) {
        $rootScope.datasett[3] = promise.data;
    });


    // Henter regioner og fylker
    $rootScope.omrade = {};
    $rootScope.omrade.region = [];
    $rootScope.omrade.fylke = [];

    nvdb.regioner().then(function(promise) {
        var regioner = promise.data.regioner;
        for (var i = 0; i < regioner.length; i++) {
            $rootScope.omrade.region.push({
                'navn': regioner[i].navn,
                'nr': regioner[i].nummer
            });
        }
    });

    $rootScope.fylker = [];
    nvdb.fylker().then(function(promise) {
        var fylker = promise.data.fylker;
        for (var i = 0; i < fylker.length; i++) {
            $rootScope.fylker.push({
                'navn': fylker[i].navn,
                'nr': fylker[i].nummer
            });
        }
        $rootScope.omrade.fylke = angular.copy($rootScope.fylker);
    });


    // Kobling mellom regioner og tilhørende fylker
    $rootScope.regionfylker = {
        1: [1, 2, 3, 4, 5],
        2: [6, 7, 8, 9, 10],
        3: [11, 12, 14],
        4: [15, 50],
        5: [18, 19, 20]
    };


    // Valgbare vegkategorier
    $rootScope.vegkategorier = {};
    $rootScope.vegkategorier.er = ["E", "R"];
    $rootScope.vegkategorier.f = ["F"];
    $rootScope.vegkategorier.erf = ["E", "R", "F"];


}]);
