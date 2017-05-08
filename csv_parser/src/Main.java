/**
 * Created by Wang.Daoping on 04.05.2017.
 */

import com.opencsv.*;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

public class Main {

    static ArrayList<String> tablet_keywords = new ArrayList<>();

    public static void main(String[] args){
        ArrayList<Article> article_list = new ArrayList<>();
        ArrayList<String> feature_list = new ArrayList<>();
        ArrayList<Float> completeness_list = new ArrayList<>();

        tablet_keywords.add("Tablet");
        tablet_keywords.add("Tablet PC");
        tablet_keywords.add("TabletPC");
        tablet_keywords.add("2-in-1 Tablet");
        tablet_keywords.add("Hybrid-Tablet");
        tablet_keywords.add("Tab Samsung");

        String feature_data_path = "C:/Users/wang.daoping/Documents/feature data/";
        String tablet_article_keywords_file = feature_data_path + "tablets_article_mercateo_keywords.dat";
        String article_feature_value_file = feature_data_path + "tablets_article_feature_value.dat";

        try {
            collectTabletArticles(tablet_article_keywords_file, article_list);
            collectFeatureValues(article_list, feature_list, article_feature_value_file);
        } catch (IOException e){
            e.printStackTrace();
        }

        //findCompleteFeatures(article_list, feature_list);
        float avgCompleteness = 0;
        for(int i = 0; i < feature_list.size(); i++){
            float buf = calculateFeatureCompleteness(article_list, feature_list.get(i));
            completeness_list.add(buf);
            avgCompleteness += buf;
        }
        avgCompleteness = avgCompleteness /completeness_list.size();
        removeWeakFeatures(feature_list, completeness_list, Math.max(avgCompleteness, 30));
        removeIncompleteArticles(article_list, feature_list);

        System.out.println(article_list.size() + " articles");
        for(int i = 0; i < feature_list.size(); i++){
            System.out.println(feature_list.get(i) + "\t" + Float.toString(completeness_list.get(i)) + "%");
        }
    }

    public static void writeArticleFeatureCSV(ArrayList<Article> article_list, ArrayList<String> feature_list, ){

    }

    public static void removeWeakFeatures(ArrayList<String> feature_List, ArrayList<Float> completeness_list, float avgCompleteness){
        for(int i = 0; i < feature_List.size(); i++){
            if(completeness_list.get(i) < avgCompleteness){
                feature_List.remove(i);
                completeness_list.remove(i);
                i--;
            }
        }
    }

    public static void collectTabletArticles(String tablet_article_keywords_file, ArrayList<Article> article_list) throws IOException{
        String[] lineBuffer;

        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(tablet_article_keywords_file), "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null) {
            if(isTablet(lineBuffer[2])){
                pushList(lineBuffer[1], article_list);
            }
        }
    }

    public static float calculateFeatureCompleteness(ArrayList<Article> article_list, String feature){
        float articleNumber = article_list.size();
        float foundNum = 0;

        for(int i = 0; i < articleNumber; i++){
            for(int j = 0; j < article_list.get(i).getFeatures().size(); j++){
                if(article_list.get(i).getFeatures().get(j).getName().equals(feature)){
                    foundNum++;
                    break;
                }
            }
        }
        return (foundNum/articleNumber)*100;
    }

    public static void removeIncompleteArticles(ArrayList<Article> article_list, ArrayList<String> feature_list){
        for(int i = 0; i < article_list.size(); i++){
            boolean full = true;
            for(int j = 0; j < feature_list.size(); j++){
                for(int k = 0; k < article_list.get(i).getFeatures().size(); k++){
                    if(feature_list.get(j).equals(article_list.get(i).getFeatures().get(k).getName())){
                        break;
                    }
                    if(k == article_list.get(i).getFeatures().size() - 1){
                        full = false;
                        break;
                    }
                }
                if(full) continue;
                article_list.remove(i);
                i--;
                break;
            }
        }
    }

    public static void findCompleteFeatures(ArrayList<Article> article_list, ArrayList<String> feature_list){
        for(int i = 0; i < feature_list.size(); i++){
            boolean exists = false;
            for(int j = 0; j < article_list.size(); j++){
                for(int k = 0; k < article_list.get(j).getFeatures().size(); k++){
                    if(article_list.get(j).getFeatures().get(k).getName().equals(feature_list.get(i))){
                        exists = true;
                        break;
                    }
                }
                if(!exists){
                    feature_list.remove(i);
                    i--;
                    break;
                }
                exists = false;
            }
        }
    }

    public static void collectFeatureValues(ArrayList<Article> article_list, ArrayList<String> feature_list, String article_feature_value_file) throws IOException{
        String[] lineBuffer;

        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(article_feature_value_file), "Cp1252"), '\t', '\"', 1);
        while ((lineBuffer = reader.readNext()) != null){
            for(int i = 0; i < article_list.size(); i++){
                if(article_list.get(i).getArticleID().equals(lineBuffer[1])){
                    switch (lineBuffer.length){
                        case 3:
                            article_list.get(i).addFeature(lineBuffer[2]);
                            break;
                        case 4:
                            article_list.get(i).addFeature(lineBuffer[2], lineBuffer[3]);
                            break;
                        default:
                            System.out.println("collectFeatureValues: unexpected lineBuffer length: " + Integer.toString(lineBuffer.length));
                            System.exit(666);
                    }
                    if(!feature_list.contains(lineBuffer[2])){
                        feature_list.add(lineBuffer[2]);
                    }
                    break;
                }
            }
        }

        // Remove articles with no feature information
        for(int i = 0; i < article_list.size(); i++){
            if(article_list.get(i).getNumFeatures() == 0){
                article_list.remove(i);
                i--;
            }
        }
    }

    public static boolean pushList(String article_id, ArrayList<Article> list){
        ArrayList<String> importedArticles = new ArrayList<>();
        for(int i = 0; i < list.size(); i++){
            importedArticles.add(list.get(i).getArticleID());
        }
        if(importedArticles.contains(article_id)) return true;
        else {
            Article article = new Article(article_id);
            list.add(article);
        }
        return true;
    }

    public static boolean isTablet(String keyword){
        return tablet_keywords.contains(keyword);
    }
}
