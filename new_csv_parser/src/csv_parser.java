import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;

import java.io.*;
import java.util.*;

public class csv_parser {

    private static HashMap<String, Article> articleHashMap = new HashMap<>();
    private static HashMap<String, HashMap<String, Article>> duplicateSetHashMap = new HashMap<>();
    private static HashMap<String, Article> mergedHashMap = new HashMap<>();

    private static final String dataPath = "C:/Users/wang.daoping/Documents/new_feature_Data/dbacess/kopierpapier_keywords_data/";
    private static final String tabletsMercateoKeywordFilepath = dataPath + "kopierpapier_mercateo_keyword_data.csv";
    private static final String articleFeatureValueFilepath = dataPath + "kopierpapier_articles_features_set.csv";
    private static final String priceDataFilepath = dataPath + "kopierpapier_price_data.csv";
    private static final String brandDataFilepath = dataPath + "kopierpapier_brand_data.csv";
    private static final String duplicateFilepath = dataPath + "kopierpapier_duplicate_relation_data.csv";

    private static List<String> tabletKeywordList = new ArrayList<>();
    private static List<String> tabletFeatureList = new ArrayList<>();
    private static List<String> featureNameList = new ArrayList<>();

    private static void collectArticles() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(tabletsMercateoKeywordFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(isTablet(lineBuffer[2]) && !articleHashMap.containsKey(lineBuffer[1])) articleHashMap.put(lineBuffer[1], new Article(lineBuffer[1]));
        }
    }

    private static void collectDuplicateRelations() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(duplicateFilepath),
                "Cp1252"), '\t', '\"', 1);
        while ((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            Article article = articleHashMap.get(lineBuffer[1]);
            String setID = lineBuffer[2];
            if(!duplicateSetHashMap.containsKey(setID)){
                HashMap<String, Article> thisSetHashMap = new HashMap<>();
                thisSetHashMap.put(lineBuffer[1], article);
                duplicateSetHashMap.put(setID, thisSetHashMap);
            } else {
                duplicateSetHashMap.get(setID).put(lineBuffer[1], article);
            }
        }
    }

    private static void collectFeatureValues() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(articleFeatureValueFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!featureNameList.contains(lineBuffer[2])){
                featureNameList.add(lineBuffer[2]);
            }
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addFeature(lineBuffer[2], lineBuffer[3]);
        }
    }

    private static void collectBrandData() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(brandDataFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addFeature("brand", lineBuffer[2]);
        }
    }

    private static void collectPriceData() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(priceDataFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addPrice(Float.parseFloat(lineBuffer[2]));
        }
    }

    private static boolean isTablet(String keyword) {
        return tabletKeywordList.contains(keyword);
    }

    private static void writeRawCSV() throws IOException {
        String filename = "tablets_training_data.csv";
        CSVWriter writer = new CSVWriter(new OutputStreamWriter(new FileOutputStream(dataPath + filename),
                "Cp1252"), '\t', CSVWriter.NO_QUOTE_CHARACTER, CSVWriter.NO_ESCAPE_CHARACTER);

        StringBuilder lineBuffer = new StringBuilder("set_id\tarticle_id\tprice");
        for(String feature : featureNameList){
            lineBuffer.append("\t");
            lineBuffer.append(feature);
        }
        String[] rec = lineBuffer.toString().split("\t");
        writer.writeNext(rec);

        for(Map.Entry<String, HashMap<String, Article>> iterator : duplicateSetHashMap.entrySet()){
            for(Map.Entry<String, Article> _iterator : iterator.getValue().entrySet()){
                String id = iterator.getKey() + "\t" + _iterator.getKey() + "\t" + _iterator.getValue().getAvgPrice();
                lineBuffer = new StringBuilder(id);
                for(String featureName : featureNameList){
                    lineBuffer.append("\t");
                    lineBuffer.append(_iterator.getValue().features.get(featureName)); // care NaN!
                }
                rec = lineBuffer.toString().split("\t");
                writer.writeNext(rec);
            }
        }
        writer.close();
    }

    private static void writeMergedCSV() throws IOException {
        String filename = "kopierpapier_full_data.csv";
        CSVWriter writer = new CSVWriter(new OutputStreamWriter(new FileOutputStream(dataPath + filename),
                "Cp1252"), ',', CSVWriter.NO_QUOTE_CHARACTER, CSVWriter.NO_ESCAPE_CHARACTER);

        StringBuilder lineBuffer = new StringBuilder("set_id\tprice");
        for(String feature : featureNameList){
            lineBuffer.append("\t");
            lineBuffer.append(feature);
        }
        String[] rec = lineBuffer.toString().split("\t");
        writer.writeNext(rec);

        for(Map.Entry<String, Article> iterator : mergedHashMap.entrySet()){
            float avg_price;
            if (( avg_price= iterator.getValue().getAvgPrice()) == -1) continue;
            String id = iterator.getKey() + "\t" + Float.toString(avg_price);
            lineBuffer = new StringBuilder(id);
            for(String featureName : featureNameList){
                lineBuffer.append("\t");
                lineBuffer.append(iterator.getValue().features.get(featureName)); // care NaN!
            }
            rec = lineBuffer.toString().split("\t");
            writer.writeNext(rec);
        }

        writer.close();
    }

    private static void mergeDuplicates() throws IOException {
        for(Map.Entry<String, HashMap<String, Article>> iterator : duplicateSetHashMap.entrySet()){
            Article mergedArticle = new Article(iterator.getKey());
            for(Map.Entry<String, Article> _iterator : iterator.getValue().entrySet()){
                Article currentArticle = _iterator.getValue();
                for(Map.Entry<String, String> __iterator : currentArticle.features.entrySet()){
                    if (!mergedArticle.features.containsKey(__iterator.getKey())){
                        mergedArticle.features.put(__iterator.getKey(), __iterator.getValue());
                    } else if (!mergedArticle.features.containsValue(__iterator.getValue())){
                        //TODO
                    }
                    mergedArticle.addPrice(currentArticle.getAvgPrice());
                }
            }
            mergedHashMap.put(iterator.getKey(), mergedArticle);
        }
    }

    private static void readTrainingData(
            String filepath, List<String> brandList, List<String> formatList, List<String> farbeList, List<String> vpeList, List<String> staerkeList)
            throws IOException{
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(filepath),
                "Cp1252"), ',', '\"', 1);
        while ((lineBuffer = reader.readNext()) != null){
            if(!brandList.contains(lineBuffer[2])) brandList.add(lineBuffer[2]);
            if(!formatList.contains(lineBuffer[3])) formatList.add(lineBuffer[3]);
            if(!farbeList.contains(lineBuffer[4])) farbeList.add(lineBuffer[4]);
            if(!vpeList.contains(lineBuffer[5])) vpeList.add(lineBuffer[5]);
            if(!staerkeList.contains(lineBuffer[6])) staerkeList.add(lineBuffer[6]);
        }
        reader.close();
    }

    private static void writeTestData(
            String filepath, List<String> brandList, List<String> formatList, List<String> farbeList, List<String> vpeList, List<String> staerkeList
    ) throws IOException{
        List<String> newBrandList = new ArrayList<>();
        /*
        newBrandList.add("Clairefontaine");
        newBrandList.add("Mondi");
        newBrandList.add("Staples");
        newBrandList.add("Arjowiggins");
        */
        newBrandList.add("Xerox");
        newBrandList.add("Papyrus");
        newBrandList.add("Papier Union");
        newBrandList.add("Igepa");

        for(String brand : newBrandList){
            String filename = brand + "_evaluation_data.csv";
            CSVWriter writer = new CSVWriter(new OutputStreamWriter(new FileOutputStream(filepath + filename),
                    "Cp1252"), '\t', CSVWriter.NO_QUOTE_CHARACTER, CSVWriter.NO_ESCAPE_CHARACTER);

            StringBuilder lineBuffer = new StringBuilder("brand\tFormat\tFarbe\tVerpackungseinheit\tPapierstaerke");
            String[] rec = lineBuffer.toString().split("\t");
            writer.writeNext(rec);
            for(String format : formatList){
                for (String farbe :farbeList){
                    for (String vpe : vpeList){
                        for (String staerke : staerkeList){
                            String line = brand + "\t" + format + "\t" + farbe + "\t" + vpe + "\t" + staerke;
                            lineBuffer = new StringBuilder(line);
                            rec = lineBuffer.toString().split("\t");
                            writer.writeNext(rec);
                        }
                    }
                }
            }
            writer.close();
        }
    }

    public static void main(String[] args){
        List brandList = new ArrayList<String>();
        List formatList = new ArrayList<String>();
        List farbeList = new ArrayList<String>();
        List vpeList = new ArrayList<String>();
        List staerkeList = new ArrayList<String>();

        try {
            readTrainingData("C:/Users/wang.daoping/Documents/git/feature_evaluation/keras_regression/kopierpapier_training_enriched_cleaned_data.csv",
                    brandList, formatList, farbeList, vpeList, staerkeList);
            writeTestData("C:/Users/wang.daoping/Documents/git/feature_evaluation/keras_regression/",
                    brandList, formatList, farbeList, vpeList, staerkeList);
        } catch (IOException e){
            e.printStackTrace();
        }

        tabletKeywordList.add("Tablet");
        tabletKeywordList.add("Tablet PC");
        tabletKeywordList.add("TabletPC");
        tabletKeywordList.add("2-in-1 Tablet");
        tabletKeywordList.add("Hybrid-Tablet");
        tabletKeywordList.add("Tab Samsung");

        tabletKeywordList.add("brand");
        tabletKeywordList.add("Betriebssystem");
        tabletKeywordList.add("SpeicherkapazitÃ¤t");
        tabletKeywordList.add("Arbeitsspeicher");
        tabletKeywordList.add("CPU-Taktfrequenz");
        tabletKeywordList.add("Bilddiagonale");
        tabletKeywordList.add("AuflÃ¶sung");
        tabletKeywordList.add("Festplatte");
        tabletKeywordList.add("AkkukapazitÃ¤t");
        tabletKeywordList.add("AuflÃ¶sung Hauptkamera");
        tabletKeywordList.add("SSD-SpeicherkapazitÃ¤t");
        tabletKeywordList.add("Grafik-Controller-Serie");

        tabletKeywordList.add("Allroundpapier");
        tabletKeywordList.add("Druckerpapier");
        tabletKeywordList.add("Druckpapier");
        tabletKeywordList.add("farbiges Kopierpapier");
        tabletKeywordList.add("Farbkopierpapier");
        tabletKeywordList.add("Farblaser-papier");
        tabletKeywordList.add("Fotokopierpapier");
        tabletKeywordList.add("Ink-Jet-Druckerpapier");
        tabletKeywordList.add("Ink-Jet-Papier");
        tabletKeywordList.add("Inkjetdruckerpapier");
        tabletKeywordList.add("Kopierpapier");
        tabletKeywordList.add("Kopierpapier farbig");
        tabletKeywordList.add("Laserpapier");
        tabletKeywordList.add("Mehrzweckpapier");
        tabletKeywordList.add("Multifunktionspapier");
        tabletKeywordList.add("Multiprintpapier");
        tabletKeywordList.add("Officepapier");
        tabletKeywordList.add("Universalpapier");

        tabletFeatureList.add("brand");
        tabletFeatureList.add("Format");
        tabletFeatureList.add("Farbe");
        tabletFeatureList.add("Verpackungseinheit");
        tabletFeatureList.add("PapierstÃ¤rke");
        //tabletFeatureList.add("Lineatur");
        //tabletFeatureList.add("Ã¶kologie");

        featureNameList.add("brand");
/*
        try {
            collectArticles();
            collectFeatureValues();
            collectPriceData();
            collectBrandData();
            collectDuplicateRelations();
            mergeDuplicates();
            //writeRawCSV();
            writeMergedCSV();
        } catch (IOException e){
            e.printStackTrace();
        }
        System.out.println(duplicateSetHashMap.size());
        */
    }
}
